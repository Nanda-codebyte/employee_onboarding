import sqlite3
from pathlib import Path

import app as app_module
import database as database_module


def make_client(tmp_path):
    db_path = tmp_path / "test_onboarding.db"
    app_module.DB_PATH = str(db_path)
    database_module.initialize_database(str(db_path))
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_register_and_login_flow(tmp_path):
    client = make_client(tmp_path)

    register_response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Doe",
            "email": "jane@example.com",
            "password": "SecurePass123",
            "department": "Engineering",
            "role": "Developer",
        },
    )

    assert register_response.status_code == 201
    payload = register_response.get_json()
    assert payload["message"] == "Registration successful"
    assert payload["employee"]["email"] == "jane@example.com"

    conn = sqlite3.connect(app_module.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM user_checklist WHERE employee_id = ?", (payload["employee"]["id"],))
    checklist_count = cursor.fetchone()[0]
    conn.close()

    assert checklist_count > 0

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "jane@example.com",
            "password": "SecurePass123",
        },
    )

    assert login_response.status_code == 200
    login_payload = login_response.get_json()
    assert login_payload["message"] == "Login successful"
    assert login_payload["employee"]["email"] == "jane@example.com"
