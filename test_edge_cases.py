"""
Edge case tests for the Employee Onboarding System
Tests: Department switching, file uploads, and AI fallback behavior
"""

import sqlite3
import os
from io import BytesIO

import app as app_module
import database as database_module


def make_client(tmp_path):
    db_path = tmp_path / "test_edge_cases.db"
    app_module.DB_PATH = str(db_path)
    database_module.initialize_database(str(db_path))
    app_module.app.config["TESTING"] = True
    app_module.UPLOAD_FOLDER = str(tmp_path / "uploads")
    os.makedirs(app_module.UPLOAD_FOLDER, exist_ok=True)
    app_module.app.config["UPLOAD_FOLDER"] = app_module.UPLOAD_FOLDER
    return app_module.app.test_client(), str(db_path)


def test_department_tasks_assignment(tmp_path):
    """Test that employees get correct department-specific tasks"""
    client, db_path = make_client(tmp_path)

    # Register Engineering employee
    eng_response = client.post(
        "/api/auth/register",
        json={
            "name": "Bob Engineer",
            "email": "bob@example.com",
            "password": "SecurePass123",
            "department": "Engineering",
            "role": "Senior Developer",
        },
    )
    assert eng_response.status_code == 201
    eng_id = eng_response.get_json()["employee"]["id"]

    # Register Sales employee
    sales_response = client.post(
        "/api/auth/register",
        json={
            "name": "Sally Sales",
            "email": "sally@example.com",
            "password": "SecurePass123",
            "department": "Sales",
            "role": "Sales Representative",
        },
    )
    assert sales_response.status_code == 201
    sales_id = sales_response.get_json()["employee"]["id"]

    # Verify both employees have tasks
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM user_checklist WHERE employee_id = ?",
        (eng_id,),
    )
    eng_tasks_count = cursor.fetchone()[0]
    assert eng_tasks_count > 0, "Engineering employee should have tasks"

    cursor.execute(
        "SELECT COUNT(*) FROM user_checklist WHERE employee_id = ?",
        (sales_id,),
    )
    sales_tasks_count = cursor.fetchone()[0]
    assert sales_tasks_count > 0, "Sales employee should have tasks"

    conn.close()


def test_file_upload_success(tmp_path):
    """Test successful file upload"""
    client, db_path = make_client(tmp_path)

    # Create employee
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Charlie Upload",
            "email": "charlie@example.com",
            "password": "SecurePass123",
            "department": "HR",
            "role": "Coordinator",
        },
    )
    employee_id = reg_response.get_json()["employee"]["id"]

    # Upload file
    file_data = BytesIO(b"Test file content")
    upload_response = client.post(
        "/api/upload",
        data={
            "file": (file_data, "onboarding_form.txt"),
            "employee_id": employee_id,
            "task_id": 1,
        },
    )

    assert upload_response.status_code == 200
    payload = upload_response.get_json()
    assert payload["message"] == "File uploaded successfully"
    assert "onboarding_form.txt" in payload["filename"]


def test_file_upload_missing_file(tmp_path):
    """Test file upload without selecting a file"""
    client, db_path = make_client(tmp_path)

    # Create employee
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Dana Upload",
            "email": "dana@example.com",
            "password": "SecurePass123",
            "department": "Finance",
            "role": "Analyst",
        },
    )
    employee_id = reg_response.get_json()["employee"]["id"]

    # Try upload without file
    upload_response = client.post(
        "/api/upload",
        data={
            "employee_id": employee_id,
            "task_id": 1,
        },
    )

    assert upload_response.status_code == 400
    payload = upload_response.get_json()
    assert "No file selected" in payload["message"]


def test_file_upload_empty_filename(tmp_path):
    """Test file upload with empty filename"""
    client, db_path = make_client(tmp_path)

    # Create employee
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Eve Upload",
            "email": "eve@example.com",
            "password": "SecurePass123",
            "department": "Marketing",
            "role": "Coordinator",
        },
    )
    employee_id = reg_response.get_json()["employee"]["id"]

    # Upload empty filename
    file_data = BytesIO(b"Test content")
    upload_response = client.post(
        "/api/upload",
        data={
            "file": (file_data, ""),
            "employee_id": employee_id,
            "task_id": 1,
        },
    )

    assert upload_response.status_code == 400
    payload = upload_response.get_json()
    assert "Please choose a file" in payload["message"]


def test_ai_fallback_no_matching_policy(tmp_path):
    """Test AI fallback when query doesn't match any policy"""
    client, db_path = make_client(tmp_path)

    # Create employee
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Frank AI",
            "email": "frank@example.com",
            "password": "SecurePass123",
            "department": "Engineering",
            "role": "Developer",
        },
    )
    employee_id = reg_response.get_json()["employee"]["id"]

    # Query with no matching policy - using words guaranteed not in policies
    ai_response = client.post(
        "/api/ai/query",
        json={
            "message": "xyzabc123 nonexistent query qwerty",
            "employee_id": employee_id,
        },
    )

    assert ai_response.status_code == 200
    payload = ai_response.get_json()
    response_data = payload["response"]
    assert response_data["source"] == "local"
    # Fallback message includes helpful onboarding-related content
    response_text = response_data["answer"].lower()
    assert response_text  # Response should not be empty
    # Should mention onboarding-related topics since no match was found
    assert "help" in response_text or "onboarding" in response_text or "policies" in response_text


def test_ai_policy_matching(tmp_path):
    """Test AI correctly matches policy keywords"""
    client, db_path = make_client(tmp_path)

    # Create employee
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Grace AI",
            "email": "grace@example.com",
            "password": "SecurePass123",
            "department": "Sales",
            "role": "Representative",
        },
    )
    employee_id = reg_response.get_json()["employee"]["id"]

    # Query matching time off policy
    ai_response = client.post(
        "/api/ai/query",
        json={
            "message": "How do I request time off or vacation?",
            "employee_id": employee_id,
        },
    )

    assert ai_response.status_code == 200
    payload = ai_response.get_json()
    response_data = payload["response"]
    assert response_data["source"] == "local"
    # Should match time off policy and return policy-related content
    assert ("leave" in response_data["answer"].lower() or 
            "request" in response_data["answer"].lower() or
            "approval" in response_data["answer"].lower())


def test_ai_includes_employee_context(tmp_path):
    """Test AI response includes employee context (department, tasks)"""
    client, db_path = make_client(tmp_path)

    # Create employee with specific department
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Henry Context",
            "email": "henry@example.com",
            "password": "SecurePass123",
            "department": "Engineering",
            "role": "Tech Lead",
        },
    )
    employee_id = reg_response.get_json()["employee"]["id"]

    # Query
    ai_response = client.post(
        "/api/ai/query",
        json={
            "message": "Tell me about our policies",
            "employee_id": employee_id,
        },
    )

    assert ai_response.status_code == 200
    payload = ai_response.get_json()
    response_data = payload["response"]
    # Response should include department context when employee_id is provided
    assert "Engineering" in response_data["answer"] or "department" in response_data["answer"].lower()


def test_task_update_after_upload(tmp_path):
    """Test updating task status after file upload"""
    client, db_path = make_client(tmp_path)

    # Create employee
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Iris Upload",
            "email": "iris@example.com",
            "password": "SecurePass123",
            "department": "Operations",
            "role": "Manager",
        },
    )
    employee_id = reg_response.get_json()["employee"]["id"]

    # Create an HR actor, since only HR can modify checklist items
    hr_response = client.post(
        "/api/auth/register",
        json={
            "name": "Hana HR",
            "email": "hana.hr@example.com",
            "password": "SecurePass123",
            "department": "HR",
            "role": "HR",
        },
    )
    hr_id = hr_response.get_json()["employee"]["id"]

    # Get first task
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT task_id FROM user_checklist WHERE employee_id = ? LIMIT 1",
        (employee_id,),
    )
    task_id = cursor.fetchone()[0]
    conn.close()

    # Upload file
    file_data = BytesIO(b"Document content")
    upload_response = client.post(
        "/api/upload",
        data={
            "file": (file_data, "document.pdf"),
            "employee_id": employee_id,
            "task_id": task_id,
        },
    )
    assert upload_response.status_code == 200

    # Update task to completed
    update_response = client.put(
        f"/api/checklist/{task_id}",
        json={
            "employee_id": employee_id,
            "actor_id": hr_id,
            "status": "Completed",
        },
    )
    assert update_response.status_code == 200

    # Verify task status
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT status FROM user_checklist WHERE employee_id = ? AND task_id = ?",
        (employee_id, task_id),
    )
    status = cursor.fetchone()[0]
    conn.close()
    assert status == "Completed"


def test_progress_includes_uploads(tmp_path):
    """Test progress endpoint includes file upload count"""
    client, db_path = make_client(tmp_path)

    # Create employee
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Jack Progress",
            "email": "jack@example.com",
            "password": "SecurePass123",
            "department": "HR",
            "role": "Specialist",
        },
    )
    employee_id = reg_response.get_json()["employee"]["id"]

    # Upload file
    file_data = BytesIO(b"File content")
    client.post(
        "/api/upload",
        data={
            "file": (file_data, "progress_file.txt"),
            "employee_id": employee_id,
            "task_id": 1,
        },
    )

    # Get progress
    progress_response = client.get(f"/api/progress/{employee_id}")
    assert progress_response.status_code == 200
    payload = progress_response.get_json()
    assert payload["uploaded_files"] >= 1
    assert payload["department"] == "HR"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
