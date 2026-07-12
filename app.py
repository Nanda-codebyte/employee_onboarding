from flask import Flask, jsonify, request, Response, send_file, session
import sqlite3
import os
import json
import re
import time
import threading
from functools import wraps

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from database import initialize_database

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or "dev-secret-key-change-in-production"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_PATH = os.path.join(os.path.dirname(__file__), "onboarding.db")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

initialize_database(DB_PATH)


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "employee_id" not in session:
            return jsonify({"message": "Authentication required"}), 401
        return f(*args, **kwargs)
    return wrapper


def hr_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "employee_id" not in session:
            return jsonify({"message": "Authentication required"}), 401

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM employees WHERE id = ?", (session["employee_id"],))
        row = cursor.fetchone()
        conn.close()

        if row is None or (row[0] or "").strip().lower() != "hr":
            return jsonify({"message": "Only HR can perform this action"}), 403

        return f(*args, **kwargs)
    return wrapper


def is_hr_session():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM employees WHERE id = ?", (session.get("employee_id"),))
    row = cursor.fetchone()
    conn.close()
    return row is not None and (row[0] or "").strip().lower() == "hr"


SSE_CLIENTS = []


def broadcast_event(event_name, payload):
    message = f"event: {event_name}\ndata: {json.dumps(payload)}\n\n"
    dead_clients = []
    for client in SSE_CLIENTS:
        try:
            client.send(message.encode("utf-8"))
        except Exception:
            dead_clients.append(client)
    for client in dead_clients:
        SSE_CLIENTS.remove(client)

POLICY_PATH = os.path.join(os.path.dirname(__file__), "policies.json")

if not os.path.exists(POLICY_PATH):
    with open(POLICY_PATH, "w", encoding="utf-8") as policy_file:
        json.dump([
            {
                "title": "Time Off Policy",
                "keywords": ["time off", "vacation", "leave", "pto"],
                "content": "Submit your leave request through HR and await manager approval."
            },
            {
                "title": "Remote Work Policy",
                "keywords": ["remote", "work from home", "wfh"],
                "content": "Remote work requests should be discussed with your manager and approved in advance."
            },
            {
                "title": "Equipment Policy",
                "keywords": ["equipment", "laptop", "device", "office gear"],
                "content": "Equipment requests are handled by IT and require manager approval."
            }
        ], policy_file, indent=2)


def load_policies():
    with open(POLICY_PATH, "r", encoding="utf-8") as policy_file:
        return json.load(policy_file)


def get_local_response(query, employee_profile, pending_tasks):
    policies = load_policies()
    normalized_query = re.sub(r"[^a-z0-9]+", " ", query.lower()).strip()
    best_match = None
    best_score = 0

    for policy in policies:
        keywords = [word.lower() for word in policy.get("keywords", [])]
        text = " ".join([policy.get("title", "").lower(), *keywords, policy.get("content", "").lower()])
        score = 0
        for word in normalized_query.split():
            if word in text:
                score += 3
        for keyword in keywords:
            if keyword in normalized_query:
                score += 5
        if policy.get("title", "").lower() in normalized_query:
            score += 6
        if score > best_score:
            best_score = score
            best_match = policy

    if best_match is None:
        return {
            "answer": "I can help with onboarding policies, remote work, equipment requests, and time off.",
            "source": "local"
        }

    context_note = ""
    if employee_profile:
        context_note = f" I see you are in {employee_profile.get('department', 'your department')} and your current tasks include {', '.join(pending_tasks[:3]) if pending_tasks else 'no pending tasks'}."

    return {
        "answer": f"{best_match['content']}{context_note}",
        "source": "local"
    }


@app.route("/api/admin/employees", methods=["GET"])
@login_required
def admin_employees():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, department, role
        FROM employees
        ORDER BY id
    """)
    employees = cursor.fetchall()

    summary = []
    for employee in employees:
        if (employee[4] or "").strip().lower() == "hr":
            continue

        employee_id = employee[0]
        cursor.execute("SELECT COUNT(*) FROM user_checklist WHERE employee_id = ?", (employee_id,))
        total_tasks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_checklist WHERE employee_id = ? AND status = 'Completed'", (employee_id,))
        completed_tasks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM user_checklist WHERE employee_id = ? AND status = 'Pending'", (employee_id,))
        pending_tasks = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM file_uploads WHERE employee_id = ?", (employee_id,))
        uploaded_files = cursor.fetchone()[0]

        completion_percentage = 0
        if total_tasks:
            completion_percentage = round((completed_tasks / total_tasks) * 100, 2)

        summary.append({
            "id": employee_id,
            "name": employee[1],
            "email": employee[2],
            "department": employee[3],
            "role": employee[4],
            "completion_percentage": completion_percentage,
            "pending_tasks": pending_tasks,
            "uploaded_files": uploaded_files,
        })

    conn.close()
    return jsonify(summary)


@app.route("/api/admin/remind", methods=["POST"])
@hr_required
def admin_remind():
    data = request.get_json(silent=True) or {}
    employee_id = data.get("employee_id")
    message = (data.get("message") or "Please complete your onboarding tasks").strip()

    if employee_id is None:
        return jsonify({"message": "employee_id is required"}), 400

    broadcast_event("reminder", {
        "employee_id": employee_id,
        "message": message,
        "timestamp": time.time(),
    })

    return jsonify({"message": "Reminder broadcasted", "employee_id": employee_id})


@app.route("/api/events")
def events():
    def generate():
        queue = []

        def send(payload):
            queue.append(payload)

        SSE_CLIENTS.append(send)
        try:
            yield "event: connected\ndata: {}\n\n".encode("utf-8")
            while True:
                if queue:
                    for item in queue:
                        yield item.encode("utf-8")
                    queue.clear()
                time.sleep(0.2)
        except GeneratorExit:
            pass
        finally:
            if send in SSE_CLIENTS:
                SSE_CLIENTS.remove(send)

    return Response(generate(), mimetype="text/event-stream")


@app.route("/api/progress/<int:employee_id>", methods=["GET"])
@login_required
def employee_progress(employee_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email, department, role FROM employees WHERE id = ?", (employee_id,))
    employee = cursor.fetchone()

    if employee is None:
        conn.close()
        return jsonify({"message": "Employee not found"}), 404

    cursor.execute("SELECT COUNT(*) FROM user_checklist WHERE employee_id = ?", (employee_id,))
    total_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM user_checklist WHERE employee_id = ? AND status = 'Completed'", (employee_id,))
    completed_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM user_checklist WHERE employee_id = ? AND status = 'Pending'", (employee_id,))
    pending_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM file_uploads WHERE employee_id = ?", (employee_id,))
    uploaded_files = cursor.fetchone()[0]

    completion_percentage = 0
    if total_tasks:
        completion_percentage = round((completed_tasks / total_tasks) * 100, 2)

    conn.close()

    return jsonify({
        "employee_id": employee_id,
        "name": employee[1],
        "email": employee[2],
        "department": employee[3],
        "role": employee[4],
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "pending_tasks": pending_tasks,
        "uploaded_files": uploaded_files,
        "completion_percentage": completion_percentage,
    })


@app.route("/api/ai/query", methods=["POST"])
def ai_query():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()
    employee_id = data.get("employee_id")

    if not message:
        return jsonify({"message": "Message is required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    employee_profile = None
    pending_tasks = []

    if employee_id is not None:
        cursor.execute(
            "SELECT id, name, email, department, role FROM employees WHERE id = ?",
            (employee_id,),
        )
        employee_row = cursor.fetchone()
        if employee_row:
            employee_profile = {
                "id": employee_row[0],
                "name": employee_row[1],
                "email": employee_row[2],
                "department": employee_row[3],
                "role": employee_row[4],
            }

        cursor.execute(
            "SELECT mt.title FROM user_checklist uc JOIN master_tasks mt ON mt.id = uc.task_id WHERE uc.employee_id = ? AND uc.status = 'Pending' ORDER BY uc.id",
            (employee_id,),
        )
        pending_tasks = [row[0] for row in cursor.fetchall()]

    conn.close()

    response = get_local_response(message, employee_profile, pending_tasks)

    return jsonify({
        "message": "AI response generated",
        "response": response
    })


@app.route("/api/policies", methods=["GET"])
def list_policies():
    return jsonify(load_policies())


@app.route("/")
def home():
    return "Employee Onboarding Assistant Backend Running"


def seed_user_checklist(employee_id, department, role=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    department_name = (department or "").strip()
    role_name = (role or "").strip()

    cursor.execute(
        """
        SELECT id
        FROM master_tasks
        WHERE (department = ? OR department = 'General')
        AND (role IS NULL OR role = '' OR role = ?)
        ORDER BY id
        """,
        (department_name, role_name),
    )

    task_ids = [row[0] for row in cursor.fetchall()]

    for task_id in task_ids:
        cursor.execute(
            """
            INSERT INTO user_checklist(employee_id, task_id, status)
            VALUES(?, ?, 'Pending')
            """,
            (employee_id, task_id),
        )

    conn.commit()
    conn.close()

    return len(task_ids)


@app.route("/api/auth/register", methods=["POST"])
def register_employee():
    data = request.get_json(silent=True) or {}

    required_fields = ["name", "email", "password", "department", "role"]
    missing_fields = [field for field in required_fields if not str(data.get(field, "")).strip()]

    if missing_fields:
        return jsonify({
            "message": "Missing required fields",
            "missing_fields": missing_fields
        }), 400

    name = data["name"].strip()
    email = data["email"].strip().lower()
    password = data["password"]
    department = data["department"].strip()
    role = data["role"].strip()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM employees WHERE email = ?", (email,))
    if cursor.fetchone() is not None:
        conn.close()
        return jsonify({
            "message": "Email already registered"
        }), 409

    hashed_password = generate_password_hash(password)

    cursor.execute(
        """
        INSERT INTO employees(name, email, password, department, role)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, email, hashed_password, department, role),
    )

    employee_id = cursor.lastrowid
    conn.commit()
    conn.close()

    seed_user_checklist(employee_id, department, role)

    session.clear()
    session["employee_id"] = employee_id

    return jsonify({
        "message": "Registration successful",
        "employee": {
            "id": employee_id,
            "name": name,
            "email": email,
            "department": department,
            "role": role
        }
    }), 201


@app.route("/api/auth/login", methods=["POST"])
def login_employee():
    data = request.get_json(silent=True) or {}

    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({
            "message": "Email and password are required"
        }), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, email, password, department, role
        FROM employees
        WHERE email = ?
        """,
        (email,),
    )

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    employee_id, name, stored_email, stored_password, department, role = row

    if not stored_password or not check_password_hash(stored_password, password):
        return jsonify({
            "message": "Invalid email or password"
        }), 401

    session.clear()
    session["employee_id"] = employee_id

    return jsonify({
        "message": "Login successful",
        "employee": {
            "id": employee_id,
            "name": name,
            "email": stored_email,
            "department": department,
            "role": role
        }
    })


@app.route("/api/auth/logout", methods=["POST"])
def logout_employee():
    session.clear()
    return jsonify({"message": "Logged out"})


@app.route("/api/auth/me", methods=["GET"])
@login_required
def current_employee():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, email, department, role FROM employees WHERE id = ?",
        (session["employee_id"],),
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        session.clear()
        return jsonify({"message": "Session is no longer valid"}), 401

    return jsonify({
        "employee": {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "department": row[3],
            "role": row[4],
        }
    })


@app.route("/api/auth/password", methods=["PUT"])
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    employee_id = data.get("employee_id")
    current_password = data.get("current_password") or ""
    new_password = data.get("new_password") or ""

    if not employee_id or not current_password or not new_password:
        return jsonify({
            "message": "employee_id, current_password and new_password are required"
        }), 400

    if int(employee_id) != session["employee_id"]:
        return jsonify({"message": "You can only change your own password"}), 403

    if len(new_password) < 6:
        return jsonify({
            "message": "New password must be at least 6 characters"
        }), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM employees WHERE id = ?", (employee_id,))
    row = cursor.fetchone()

    if row is None:
        conn.close()
        return jsonify({"message": "Employee not found"}), 404

    if not row[0] or not check_password_hash(row[0], current_password):
        conn.close()
        return jsonify({"message": "Current password is incorrect"}), 401

    cursor.execute(
        "UPDATE employees SET password = ? WHERE id = ?",
        (generate_password_hash(new_password), employee_id),
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Password updated successfully"})


@app.route("/api/checklist/<int:employee_id>", methods=["GET"])
@login_required
def get_checklist(employee_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            mt.id,
            mt.title,
            mt.priority,
            mt.due_day,
            uc.status,
            mt.category,
            mt.task_type,
            mt.description

        FROM master_tasks mt

        JOIN user_checklist uc
        ON mt.id = uc.task_id

        WHERE uc.employee_id = ?
    """, (employee_id,))

    rows = cursor.fetchall()

    conn.close()

    checklist = []

    for row in rows:
        checklist.append({
            "id": row[0],
            "title": row[1],
            "priority": row[2],
            "due_day": row[3],
            "status": row[4],
            "category": row[5] or "General",
            "task_type": row[6] or "checklist",
            "description": row[7]
        })

    return jsonify(checklist)


@app.route("/api/checklist/<int:task_id>", methods=["PUT"])
@hr_required
def update_task(task_id):
    data = request.get_json(silent=True) or {}
    employee_id = data.get("employee_id")

    if employee_id is None:
        return jsonify({"message": "employee_id is required"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT status
        FROM user_checklist
        WHERE task_id = ? AND employee_id = ?
    """, (task_id, employee_id))

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return jsonify({"message": "Task not found"}), 404

    requested_status = data.get("status")
    if requested_status in ("Completed", "Pending"):
        new_status = requested_status
    elif row[0] == "Pending":
        new_status = "Completed"
    else:
        new_status = "Pending"

    cursor.execute("""
        UPDATE user_checklist
        SET status = ?
        WHERE task_id = ? AND employee_id = ?
    """, (new_status, task_id, employee_id))

    conn.commit()
    conn.close()

    return jsonify({
        "message": "Task Updated Successfully",
        "status": new_status
    })


@app.route("/api/upload", methods=["POST"])
@login_required
def upload_file():

    if "file" not in request.files:
        return jsonify({
            "message": "No file selected"
        }), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({
            "message": "Please choose a file"
        }), 400

    employee_id = request.form.get("employee_id")
    task_id = request.form.get("task_id")

    if employee_id and int(employee_id) != session["employee_id"] and not is_hr_session():
        return jsonify({"message": "You can only upload documents for yourself"}), 403

    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({
            "message": "Invalid file name"
        }), 400

    unique_filename = f"{int(time.time() * 1000)}_{filename}"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    file.save(filepath)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO file_uploads
        (
            employee_id,
            task_id,
            filename,
            filepath
        )
        VALUES (?, ?, ?, ?)
    """, (
        employee_id,
        task_id,
        filename,
        filepath
    ))

    if employee_id and task_id:
        cursor.execute("SELECT task_type FROM master_tasks WHERE id = ?", (task_id,))
        task_row = cursor.fetchone()
        if task_row and (task_row[0] or "").strip().lower() == "upload":
            cursor.execute(
                "UPDATE user_checklist SET status = 'Completed' WHERE employee_id = ? AND task_id = ?",
                (employee_id, task_id),
            )

    conn.commit()
    conn.close()

    return jsonify({
        "message": "File uploaded successfully",
        "filename": filename
    })


@app.route("/api/uploads/<int:employee_id>", methods=["GET"])
@login_required
def list_uploads(employee_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            fu.id,
            fu.filename,
            fu.task_id,
            fu.upload_date,
            mt.title
        FROM file_uploads fu
        LEFT JOIN master_tasks mt ON mt.id = fu.task_id
        WHERE fu.employee_id = ?
        ORDER BY fu.upload_date DESC
    """, (employee_id,))

    rows = cursor.fetchall()
    conn.close()

    uploads = [
        {
            "id": row[0],
            "filename": row[1],
            "task_id": row[2],
            "upload_date": row[3],
            "task_title": row[4],
        }
        for row in rows
    ]

    return jsonify(uploads)


@app.route("/api/uploads/download/<int:upload_id>", methods=["GET"])
@login_required
def download_upload(upload_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT filepath, filename FROM file_uploads WHERE id = ?", (upload_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({"message": "File not found"}), 404

    filepath, filename = row

    if not os.path.exists(filepath):
        return jsonify({"message": "File no longer available"}), 404

    return send_file(filepath, as_attachment=True, download_name=filename)


@app.route("/api/quiz/<int:task_id>", methods=["GET"])
def get_quiz(task_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            question,
            option1,
            option2,
            option3,
            option4

        FROM quizzes

        WHERE task_id = ?
    """, (task_id,))

    quiz = cursor.fetchone()

    conn.close()

    if quiz is None:
        return jsonify({
            "message": "Quiz not found"
        }), 404

    return jsonify({
        "question": quiz[0],
        "options": [
            quiz[1],
            quiz[2],
            quiz[3],
            quiz[4]
        ]
    })


@app.route("/api/quiz/<int:task_id>", methods=["POST"])
@login_required
def submit_quiz(task_id):

    data = request.get_json()

    if not data or "answer" not in data:
        return jsonify({
            "message": "Answer is required"
        }), 400

    answer = data["answer"]
    employee_id = data.get("employee_id")

    if employee_id is not None and int(employee_id) != session["employee_id"]:
        return jsonify({"message": "You can only submit your own quiz"}), 403

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT correct_answer
        FROM quizzes
        WHERE task_id = ?
    """, (task_id,))

    row = cursor.fetchone()

    if row is None:
        conn.close()

        return jsonify({
            "message": "Quiz not found"
        }), 404

    correct_answer = row[0]

    passed = answer.strip().lower() == correct_answer.strip().lower()

    if passed and employee_id is not None:
        cursor.execute(
            "UPDATE user_checklist SET status = 'Completed' WHERE employee_id = ? AND task_id = ?",
            (employee_id, task_id),
        )
        conn.commit()

    conn.close()

    if passed:
        return jsonify({
            "passed": True,
            "message": "Quiz Passed"
        })

    return jsonify({
        "passed": False,
        "message": "Incorrect Answer"
    })


if __name__ == "__main__":
    app.run(debug=True)