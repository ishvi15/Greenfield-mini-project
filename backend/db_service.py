from src.hr_analytics.db_manager import DatabaseConnection

last_insert_error = ""


def get_last_insert_error() -> str:
    return last_insert_error


def insert_employee_record(
    first_name: str, last_name: str, department: str, role: str, salary: float
) -> bool:
    """Insert an employee into the OLTP database."""
    global last_insert_error
    last_insert_error = ""
    if not first_name or not last_name or not department or not role:
        last_insert_error = "First name, last name, department, and role are required."
        return False
    conn = None
    try:
        conn = DatabaseConnection().get_connection()
        cursor = conn.cursor()
        email = f"{first_name.lower()}.{last_name.lower()}@company.local"
        cursor.execute(
            """
            INSERT INTO employees
                (first_name, last_name, email, department, role_name, salary, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s, CURDATE())
            """,
            (
                first_name.strip(), last_name.strip(), email,
                department, role.strip(), float(salary)
            ),
        )
        conn.commit()
        return True
    except Exception as exc:
        if conn is not None:
            conn.rollback()
        last_insert_error = str(exc)
        return False


def insert_project_record(
    project_name: str, department: str, priority: str, allocated_hours: float
) -> bool:
    """Insert a project into the OLTP database."""
    if not project_name or not department:
        return False
    try:
        conn = DatabaseConnection().get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO projects
                (project_name, department, priority_level, budget, start_date)
            VALUES (%s, %s, %s, %s, CURDATE())
            """,
            (project_name.strip(), department, priority, float(allocated_hours * 100)),
        )
        conn.commit()
        return True
    except Exception:
        return False


def insert_review_record(employee_id: int, score: float, department: str) -> bool:
    """Insert a performance review into the OLTP database."""
    if not employee_id or not department:
        return False
    try:
        conn = DatabaseConnection().get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reviews
                (employee_id, review_date, performance_score, manager_comment, department)
            VALUES (%s, CURDATE(), %s, %s, %s)
            """,
            (
                int(employee_id), float(score),
                "Submitted from dashboard form", department
            ),
        )
        conn.commit()
        return True
    except Exception:
        return False
