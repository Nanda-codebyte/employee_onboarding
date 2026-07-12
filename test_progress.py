import app as app_module
import database as database_module


def make_client(tmp_path):
    db_path = tmp_path / "test_progress.db"
    app_module.DB_PATH = str(db_path)
    database_module.initialize_database(str(db_path))
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_progress_summary(tmp_path):
    client = make_client(tmp_path)

    conn = app_module.sqlite3.connect(app_module.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees(name, email, password, department, role) VALUES (?, ?, ?, ?, ?)",
        ("Dana", "dana@example.com", "secret", "Sales", "Associate"),
    )
    employee_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO master_tasks(title, department, priority, due_day) VALUES (?, ?, ?, ?)",
        ("Intro Training", "Sales", "High", 2),
    )
    task_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO user_checklist(employee_id, task_id, status) VALUES (?, ?, ?)",
        (employee_id, task_id, "Completed"),
    )
    conn.commit()
    conn.close()

    with client.session_transaction() as flask_session:
        flask_session["employee_id"] = employee_id

    response = client.get(f"/api/progress/{employee_id}")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["employee_id"] == employee_id
    assert payload["completed_tasks"] >= 1
    assert payload["pending_tasks"] >= 0
