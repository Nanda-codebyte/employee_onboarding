import sqlite3

import app as app_module
import database as database_module


def make_client(tmp_path):
    db_path = tmp_path / "test_onboarding.db"
    app_module.DB_PATH = str(db_path)
    database_module.initialize_database(str(db_path))
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_ai_query_returns_policy_guidance(tmp_path):
    client = make_client(tmp_path)

    conn = sqlite3.connect(app_module.DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO employees(name, email, password, department, role) VALUES (?, ?, ?, ?, ?)",
        ("Ava", "ava@example.com", "secret", "Engineering", "Developer"),
    )
    employee_id = cursor.lastrowid
    cursor.execute(
        "INSERT INTO user_checklist(employee_id, task_id, status) VALUES (?, ?, ?)",
        (employee_id, 1, "Pending"),
    )
    conn.commit()
    conn.close()

    response = client.post(
        "/api/ai/query",
        json={
            "message": "How do I request time off?",
            "employee_id": employee_id,
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert "response" in payload
    assert isinstance(payload["response"], dict)
    assert payload["response"]["source"] in {"openai", "local"}
