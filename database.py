import os
import sqlite3


DEFAULT_DB_PATH = os.path.join(os.path.dirname(__file__), "onboarding.db")


def initialize_database(db_path=None):
    db_path = db_path or DEFAULT_DB_PATH
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT,
            department TEXT NOT NULL,
            role TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS master_tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            department TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_day INTEGER
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS file_uploads(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            task_id INTEGER,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(employee_id) REFERENCES employees(id),
            FOREIGN KEY(task_id) REFERENCES master_tasks(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_checklist(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER,
            task_id INTEGER,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY(employee_id) REFERENCES employees(id),
            FOREIGN KEY(task_id) REFERENCES master_tasks(id)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS quizzes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            question TEXT NOT NULL,
            option1 TEXT,
            option2 TEXT,
            option3 TEXT,
            option4 TEXT,
            correct_answer TEXT
        )
        """
    )

    columns = {row[1] for row in cursor.execute("PRAGMA table_info(employees)").fetchall()}
    if "email" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN email TEXT")
    if "password" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN password TEXT")
    if "department" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN department TEXT")
    if "role" not in columns:
        cursor.execute("ALTER TABLE employees ADD COLUMN role TEXT")

    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_employees_email ON employees(email)")

    task_columns = {row[1] for row in cursor.execute("PRAGMA table_info(master_tasks)").fetchall()}
    if "category" not in task_columns:
        cursor.execute("ALTER TABLE master_tasks ADD COLUMN category TEXT DEFAULT 'General'")
    if "task_type" not in task_columns:
        cursor.execute("ALTER TABLE master_tasks ADD COLUMN task_type TEXT DEFAULT 'checklist'")
    if "description" not in task_columns:
        cursor.execute("ALTER TABLE master_tasks ADD COLUMN description TEXT")
    if "role" not in task_columns:
        cursor.execute("ALTER TABLE master_tasks ADD COLUMN role TEXT")

    cursor.execute("SELECT COUNT(*) FROM master_tasks")
    if cursor.fetchone()[0] == 0:
        tasks = [
            ("Set up Direct Deposit", "General", "High", 1, "HR & Compliance", "upload", "Upload a voided check or bank letter so payroll can set up direct deposit.", None),
            ("Sign NDA", "General", "High", 1, "HR & Compliance", "upload", "Review and upload your signed non-disclosure agreement.", None),
            ("Complete I-9 Verification", "General", "High", 1, "HR & Compliance", "upload", "Upload proof of identity and work authorization documents.", None),
            ("Meet Your Manager", "General", "Medium", 1, "General", "checklist", "Schedule a 1:1 with your manager to align on goals for your first month.", None),
            ("IT Security Awareness Training", "General", "High", 2, "IT Setup", "quiz", "Complete the short security awareness quiz before accessing company systems.", None),
            ("Benefits Enrollment", "General", "Medium", 3, "HR & Compliance", "checklist", "Review and select your health, dental, and retirement benefits.", None),
            ("Gain GitHub Access", "Engineering", "High", 2, "IT Setup", "checklist", "Request access to the engineering GitHub organization.", None),
            ("Configure Development Environment", "Engineering", "Medium", 2, "IT Setup", "checklist", "Install the toolchain and clone the starter repositories.", None),
            ("Set Up VPN / SSO Access", "Engineering", "High", 2, "IT Setup", "checklist", "Install the VPN client and enroll in single sign-on.", None),
            ("Complete Code Review Training", "Engineering", "Medium", 3, "IT Setup", "quiz", "Take the short quiz on the team's code review standards.", None),
            ("Set Up 1:1 Cadence With Reports", "Engineering", "Medium", 3, "General", "checklist", "Schedule recurring 1:1s with each of your direct reports.", "Engineering Manager"),
            ("CRM Training", "Sales", "Medium", 2, "Sales Enablement", "checklist", "Complete the CRM walkthrough course.", None),
            ("Product Training", "Sales", "High", 3, "Sales Enablement", "checklist", "Attend product training sessions with the enablement team.", None),
            ("Shadow a Sales Call", "Sales", "Medium", 3, "Sales Enablement", "checklist", "Join a live customer call with a senior rep.", None),
            ("Set Up CRM Dashboard", "Sales", "Low", 4, "Sales Enablement", "checklist", "Configure your personal CRM dashboard and pipeline views.", None),
            ("Review Team Pipeline Dashboard", "Sales", "Medium", 3, "Sales Enablement", "checklist", "Review your team's pipeline reporting dashboard and forecasting cadence.", "Sales Manager"),
            ("Company Policies", "HR", "High", 1, "HR & Compliance", "quiz", "Read the employee handbook, then pass the short policy quiz.", None),
            ("Review Employee Handbook", "HR", "High", 2, "HR & Compliance", "checklist", "Read through the full employee handbook.", None),
            ("Complete Diversity & Inclusion Training", "HR", "Medium", 3, "HR & Compliance", "quiz", "Complete the D&I training module and quiz.", None),
            ("Set Up Applicant Tracking System Access", "HR", "Medium", 2, "IT Setup", "checklist", "Request access to the applicant tracking system used for hiring.", "HR"),
            ("Brand Guidelines Review", "Design", "High", 2, "Design", "checklist", "Review the brand and design system guidelines.", None),
            ("Set Up Design Tools Access (Figma)", "Design", "High", 2, "IT Setup", "checklist", "Request access to the team's Figma workspace.", None),
            ("Review Team Critique Process", "Design", "Medium", 3, "Design", "checklist", "Review how design critiques are run and schedule the next one.", "Design Lead"),
        ]
        cursor.executemany(
            """
            INSERT INTO master_tasks(title, department, priority, due_day, category, task_type, description, role)
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tasks,
        )

    cursor.execute("SELECT COUNT(*) FROM quizzes")
    if cursor.fetchone()[0] == 0:
        quizzes_by_task_title = [
            ("Company Policies", "Where should you go to review company policies before you have questions?", "The employee handbook", "A coworker's desk", "Social media", "Guessing", "The employee handbook"),
            ("IT Security Awareness Training", "What should you do before accessing company systems?", "Share your password", "Complete security awareness training", "Ignore security training", "Use someone else's account", "Complete security awareness training"),
            ("Complete Code Review Training", "What is the primary goal of a code review?", "Slow down releases", "Catch bugs and share knowledge before merging", "Assign blame", "Increase line count", "Catch bugs and share knowledge before merging"),
            ("Complete Diversity & Inclusion Training", "What is one benefit of workplace diversity training?", "It teaches you to ignore differences", "It builds awareness and a more inclusive team culture", "It is only for managers", "It replaces performance reviews", "It builds awareness and a more inclusive team culture"),
        ]
        for title, question, option1, option2, option3, option4, correct_answer in quizzes_by_task_title:
            cursor.execute("SELECT id FROM master_tasks WHERE title = ?", (title,))
            task_row = cursor.fetchone()
            if task_row:
                cursor.execute(
                    """
                    INSERT INTO quizzes(task_id, question, option1, option2, option3, option4, correct_answer)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (task_row[0], question, option1, option2, option3, option4, correct_answer),
                )

    conn.commit()
    conn.close()




    return db_path