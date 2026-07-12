import app as app_module
import database as database_module


def make_client(tmp_path):
    db_path = tmp_path / "test_onboarding.db"
    app_module.DB_PATH = str(db_path)
    database_module.initialize_database(str(db_path))
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_admin_and_sse_flow(tmp_path):
    client = make_client(tmp_path)

    conn = app_module.sqlite3.connect(app_module.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees(name, email, password, department, role) VALUES (?, ?, ?, ?, ?)",
        ("Ada", "ada@example.com", "secret", "Engineering", "Developer"),
    )
    employee_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO master_tasks(title, department, priority, due_day) VALUES (?, ?, ?, ?)",
        ("Policy Review", "Engineering", "High", 3),
    )
    task_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO user_checklist(employee_id, task_id, status) VALUES (?, ?, ?)",
        (employee_id, task_id, "Pending"),
    )
    cursor.execute(
        "INSERT INTO file_uploads(employee_id, task_id, filename, filepath) VALUES (?, ?, ?, ?)",
        (employee_id, task_id, "doc.txt", "/tmp/doc.txt"),
    )
    cursor.execute(
        "INSERT INTO employees(name, email, password, department, role) VALUES (?, ?, ?, ?, ?)",
        ("Hana HR", "hana@example.com", "secret", "HR", "HR"),
    )
    hr_id = cursor.lastrowid
    conn.commit()
    conn.close()

    with client.session_transaction() as flask_session:
        flask_session["employee_id"] = hr_id

    admin_response = client.get("/api/admin/employees")
    assert admin_response.status_code == 200
    admin_payload = admin_response.get_json()
    assert admin_payload[0]["id"] == employee_id
    assert admin_payload[0]["pending_tasks"] >= 1

    with client.get("/api/events", buffered=False) as sse_response:
        assert sse_response.status_code == 200
        first_chunk = next(sse_response.response)
        assert b"event:" in first_chunk

    reminder_response = client.post(
        "/api/admin/remind",
        json={"employee_id": employee_id, "message": "Please complete your onboarding tasks"},
    )
    assert reminder_response.status_code == 200
