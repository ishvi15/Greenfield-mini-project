import os
from pathlib import Path

import mysql.connector
import pandas as pd
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
BATCH_SIZE = 500


def env_setting(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip().strip('"').strip("'")


def source_id(value: object, prefix: str) -> int:
    return int(str(value).replace(prefix, "").lstrip("0") or "0")


def insert_batches(cursor, query: str, rows: list[tuple], label: str) -> None:
    for start in range(0, len(rows), BATCH_SIZE):
        cursor.executemany(query, rows[start:start + BATCH_SIZE])
        print(f"{label}: {min(start + BATCH_SIZE, len(rows))}/{len(rows)}", flush=True)


def main() -> None:
    load_dotenv(ROOT / ".env", override=True)
    connection = mysql.connector.connect(
        host=env_setting("MYSQL_HOST"),
        port=int(env_setting("MYSQL_PORT", "3306")),
        user=env_setting("MYSQL_USER"),
        password=env_setting("MYSQL_PASSWORD"),
        database="hr_analytics_oltp",
        connection_timeout=30,
        use_pure=True,
    )
    cursor = connection.cursor()

    employees = pd.read_csv(ROOT / "data/processed/employee_synthesized.csv")
    projects = pd.read_csv(ROOT / "data/processed/projects.csv")
    reviews = pd.read_csv(ROOT / "data/processed/performance_reviews.csv")
    assignments = pd.read_csv(ROOT / "data/processed/assignments.csv")

    employee_rows = [
        (
            int(row.EmployeeNumber),
            str(row.FirstName),
            str(row.LastName),
            str(row.Email),
            str(row.Department),
            str(row.JobRole),
            float(row.MonthlyIncome),
            str(row.HireDate),
        )
        for row in employees.itertuples()
    ]
    insert_batches(cursor,
        """
        INSERT IGNORE INTO employees
            (employee_id, first_name, last_name, email, department, role_name, salary, hire_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        employee_rows,
        "employees",
    )

    project_rows = [
        (
            source_id(row.ProjectID, "PRJ"),
            str(row.ProjectName),
            str(row.Department) if hasattr(row, "Department") else "Unknown",
            str(row.Priority),
            float(row.Budget),
            str(row.StartDate),
            None if pd.isna(row.EndDate) else str(row.EndDate),
        )
        for row in projects.itertuples()
    ]
    insert_batches(cursor,
        """
        INSERT IGNORE INTO projects
            (project_id, project_name, department, priority_level, budget, start_date, end_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        project_rows,
        "projects",
    )
    connection.commit()

    employee_departments = dict(
        zip(
            employees["EmployeeID"].astype(str).map(lambda value: source_id(value, "EMP")),
            employees["Department"].astype(str),
        )
    )
    review_query = """
        INSERT IGNORE INTO reviews
            (review_id, employee_id, review_date, performance_score, department)
        VALUES (%s, %s, %s, %s, %s)
    """
    for start in range(0, len(reviews), BATCH_SIZE):
        review_rows = [
            (
                source_id(row.ReviewID, "REV"),
                source_id(row.EmployeeID, "EMP"),
                str(row.ReviewDate),
                float(row.PerformanceScore),
                str(employee_departments[source_id(row.EmployeeID, "EMP")]),
            )
            for row in reviews.iloc[start:start + BATCH_SIZE].itertuples()
        ]
        cursor.executemany(review_query, review_rows)
        connection.commit()
        print(f"reviews: {min(start + BATCH_SIZE, len(reviews))}/{len(reviews)}", flush=True)

    assignment_rows = [
        (
            source_id(row.AssignmentID, ""),
            source_id(row.EmployeeID, "EMP"),
            source_id(row.ProjectID, "PRJ"),
            str(row.AssignmentStart),
            int(row.AllocationPercent),
        )
        for row in assignments.itertuples()
        if not pd.isna(row.AssignmentStart)
    ]
    insert_batches(cursor,
        """
        INSERT IGNORE INTO assignments
            (assignment_id, employee_id, project_id, assignment_date, allocation_percent)
        VALUES (%s, %s, %s, %s, %s)
        """,
        assignment_rows,
        "assignments",
    )

    connection.commit()
    for table in ("employees", "projects", "reviews", "assignments"):
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        print(f"{table}: {cursor.fetchone()[0]}")
    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()