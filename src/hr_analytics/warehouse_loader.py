from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import mysql.connector
import pandas as pd
from dotenv import load_dotenv


load_dotenv()


class WarehouseLoader:
    def __init__(self, connection: Any | None = None):
        self.connection = connection

    def _ensure_connection(self):
        if self.connection is None:
            config = {
                "host": os.getenv("MYSQL_WAREHOUSE_HOST", os.getenv("MYSQL_HOST", "localhost")),
                "port": int(os.getenv("MYSQL_WAREHOUSE_PORT", os.getenv("MYSQL_PORT", "3306"))),
                "user": os.getenv("MYSQL_WAREHOUSE_USER", os.getenv("MYSQL_USER", "root")),
                "password": os.getenv("MYSQL_WAREHOUSE_PASSWORD", os.getenv("MYSQL_PASSWORD", "")),
                "connection_timeout": 30,
                "use_pure": True,
                "autocommit": True,
            }
            database = os.getenv("MYSQL_WAREHOUSE_DATABASE", "hr_analytics_warehouse")
            try:
                self.connection = mysql.connector.connect(**config, database=database)
            except mysql.connector.Error as exc:
                if exc.errno != 1049:
                    raise
                bootstrap = mysql.connector.connect(**config)
                bootstrap.cursor().execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
                bootstrap.commit()
                bootstrap.close()
                self.connection = mysql.connector.connect(**config, database=database)

            cursor = self.connection.cursor()
            cursor.execute("SET SESSION innodb_lock_wait_timeout = 5")
            cursor.execute("SHOW TABLES")
            if not cursor.fetchall():
                schema_path = Path(__file__).resolve().parents[2] / "sql" / "02_olap_schema.sql"
                for statement in schema_path.read_text(encoding="utf-8").split(";"):
                    statement = statement.strip()
                    if statement and not statement.upper().startswith(("CREATE DATABASE", "USE ")):
                        cursor.execute(statement)
                self.connection.commit()
        return self.connection

    def _clear_stale_load_transactions(self) -> None:
        config = {
            "host": os.getenv("MYSQL_WAREHOUSE_HOST", os.getenv("MYSQL_HOST", "localhost")),
            "port": int(os.getenv("MYSQL_WAREHOUSE_PORT", os.getenv("MYSQL_PORT", "3306"))),
            "user": os.getenv("MYSQL_WAREHOUSE_USER", os.getenv("MYSQL_USER", "root")),
            "password": os.getenv("MYSQL_WAREHOUSE_PASSWORD", os.getenv("MYSQL_PASSWORD", "")),
            "connection_timeout": 10,
            "use_pure": True,
        }
        database = os.getenv("MYSQL_WAREHOUSE_DATABASE", "hr_analytics_warehouse")
        admin = mysql.connector.connect(**config)
        try:
            cursor = admin.cursor()
            cursor.execute(
                """
                SELECT trx_mysql_thread_id
                FROM information_schema.innodb_trx AS trx
                JOIN information_schema.processlist AS process
                  ON process.ID = trx.trx_mysql_thread_id
                WHERE process.USER = %s
                  AND process.DB = %s
                  AND trx.trx_started < NOW() - INTERVAL 30 SECOND
                """,
                (config["user"], database),
            )
            for (thread_id,) in cursor.fetchall():
                cursor.execute(f"KILL {int(thread_id)}")
        finally:
            admin.close()

    def _executemany_with_retry(self, cursor, query: str, rows, attempts: int = 4):
        for attempt in range(attempts):
            try:
                cursor.executemany(query, rows)
                return
            except mysql.connector.Error as exc:
                if exc.errno != 1205 or attempt == attempts - 1:
                    raise
                self.connection.rollback()
                cursor.execute("SET SESSION innodb_lock_wait_timeout = 5")

    def load_processed_csvs(
        self,
        employee_csv: str | Path = "data/processed/employee_synthesized.csv",
        review_csv: str | Path = "data/processed/performance_reviews.csv",
        project_csv: str | Path = "data/processed/projects.csv",
    ) -> dict[str, int]:
        """Load the processed employee history and review CSVs into the warehouse."""
        self._ensure_connection()
        self._clear_stale_load_transactions()
        project_root = Path(__file__).resolve().parents[2]
        employee_path = Path(employee_csv)
        review_path = Path(review_csv)
        project_path = Path(project_csv)
        employees = pd.read_csv(employee_path if employee_path.is_absolute() else project_root / employee_path)
        reviews = pd.read_csv(review_path if review_path.is_absolute() else project_root / review_path)
        projects = pd.read_csv(project_path if project_path.is_absolute() else project_root / project_path)
        required_employee_columns = {
            "EmployeeNumber", "Department", "JobRole", "MonthlyIncome",
            "StartDate", "EndDate", "IsCurrent", "FirstName", "LastName",
        }
        required_review_columns = {
            "ReviewID", "EmployeeID", "ReviewDate", "PerformanceScore",
        }
        required_project_columns = {
            "ProjectID", "ProjectName", "Priority", "Budget", "StartDate",
        }
        missing_employee = required_employee_columns.difference(employees.columns)
        missing_review = required_review_columns.difference(reviews.columns)
        missing_project = required_project_columns.difference(projects.columns)
        if missing_employee or missing_review or missing_project:
            raise ValueError(
                f"Missing employee columns: {sorted(missing_employee)}; "
                f"missing review columns: {sorted(missing_review)}; "
                f"missing project columns: {sorted(missing_project)}"
            )

        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM fact_performance_reviews")
        cursor.execute("DELETE FROM dim_date")
        cursor.execute("DELETE FROM dim_employee")
        cursor.execute("DELETE FROM dim_department")
        cursor.execute("DELETE FROM dim_project")

        departments = employees["Department"].fillna("Unknown").drop_duplicates().tolist()
        self._executemany_with_retry(
            cursor,
            """
            INSERT INTO dim_department
                (department_name, start_date, end_date, is_current)
            VALUES (%s, %s, %s, %s)
            """,
            [(str(department), None, None, True) for department in departments],
        )

        project_rows = []
        for _, row in projects.iterrows():
            project_id = int(str(row["ProjectID"]).replace("PRJ", "").lstrip("0") or "0")
            department = row["Department"] if "Department" in projects.columns and pd.notna(row["Department"]) else None
            project_rows.append(
                (
                    project_id,
                    str(row["ProjectName"]),
                    str(department) if department is not None else None,
                    str(row["Priority"]),
                )
            )
        self._executemany_with_retry(
            cursor,
            """
            INSERT INTO dim_project
                (project_id, project_name, department, priority_level)
            VALUES (%s, %s, %s, %s)
            """,
            project_rows,
        )
        employee_rows = []
        for _, row in employees.iterrows():
            end_date = row["EndDate"] if pd.notna(row["EndDate"]) else "9999-12-31"
            salary = pd.to_numeric(row["MonthlyIncome"], errors="coerce")
            role = row["JobRole"] if pd.notna(row["JobRole"]) else "Unknown"
            department = row["Department"] if pd.notna(row["Department"]) else "Unknown"
            employee_rows.append(
                (
                    int(row["EmployeeNumber"]),
                    f"{row['FirstName']} {row['LastName']}".strip(),
                    str(department),
                    str(role),
                    float(salary) if pd.notna(salary) else 0.0,
                    str(row["StartDate"]),
                    str(end_date),
                    bool(row["IsCurrent"]),
                )
            )
        self._executemany_with_retry(cursor,
            """
            INSERT IGNORE INTO dim_employee
                (business_key, employee_name, department, role_name, salary,
                 start_date, end_date, is_current)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            employee_rows,
        )

        cursor.execute("SELECT employee_sk, business_key FROM dim_employee")
        employee_keys = {int(business_key): int(employee_sk) for employee_sk, business_key in cursor.fetchall()}
        employee_number_by_id = {}
        if "EmployeeID" in employees.columns:
            employee_number_by_id = dict(
                zip(employees["EmployeeID"].astype(str), employees["EmployeeNumber"].astype(int))
            )

        employee_dates = pd.concat(
            [pd.to_datetime(employees["StartDate"], errors="coerce"), pd.to_datetime(employees["EndDate"], errors="coerce")]
        ).dropna().dt.date
        review_dates = pd.to_datetime(reviews["ReviewDate"]).dt.date
        all_dates = pd.Series(pd.concat([pd.Series(employee_dates), pd.Series(review_dates)]).drop_duplicates().tolist())
        self._executemany_with_retry(cursor,
            """
            INSERT IGNORE INTO dim_date
                (full_date, year_num, month_num, quarter_num, is_current_year)
            VALUES (%s, %s, %s, %s, %s)
            """,
            [
                (date_value, date_value.year, date_value.month, ((date_value.month - 1) // 3) + 1, date_value.year == pd.Timestamp.now().year)
                for date_value in all_dates
            ],
        )
        cursor.execute("SELECT date_sk, full_date FROM dim_date")
        date_keys = {date_value: int(date_sk) for date_sk, date_value in cursor.fetchall()}

        review_rows = []
        for _, row in reviews.iterrows():
            employee_reference = str(row["EmployeeID"])
            employee_id = employee_number_by_id.get(employee_reference)
            if employee_id is None:
                employee_id = int(employee_reference.replace("EMP", "").lstrip("0") or "0")
            review_date = pd.Timestamp(row["ReviewDate"]).date()
            score = float(row["PerformanceScore"])
            rating = str(row.get("PerformanceRating", ""))
            review_rows.append(
                (
                    employee_keys[employee_id],
                    date_keys[review_date],
                    int(str(row["ReviewID"]).replace("REV", "").lstrip("0") or "0"),
                    score,
                    str(employees.loc[employees["EmployeeNumber"] == employee_id, "Department"].iloc[0]),
                    rating,
                    review_date.year,
                    None,
                    str(employees.loc[employees["EmployeeNumber"] == employee_id, "Department"].iloc[0]),
                    None,
                )
            )
        self._executemany_with_retry(cursor,
            """
            INSERT IGNORE INTO fact_performance_reviews
                (employee_sk, date_sk, review_id, performance_score, department,
                 rating, review_year, employee_name, department_name, DENSE_RANK_ANALYSIS)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            review_rows,
        )
        self.connection.commit()
        return {
            "dim_department": len(departments),
            "dim_project": len(project_rows),
            "dim_employee": len(employee_rows),
            "dim_date": len(all_dates),
            "fact_performance_reviews": len(review_rows),
        }

    def load_dim_employee(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0

        self._ensure_connection()

        required = {"business_key", "employee_name", "department", "role", "salary", "start_date", "end_date", "is_current"}
        missing = required.difference(df.columns)
        if missing:
            raise ValueError(f"Missing required columns for dim_employee load: {sorted(missing)}")

        rows = [
            (
                int(row["business_key"]),
                str(row["employee_name"]),
                str(row["department"]),
                str(row["role"]),
                float(row["salary"]),
                str(row["start_date"]),
                str(row["end_date"]),
                bool(row["is_current"]),
            )
            for _, row in df.iterrows()
        ]

        cursor = self.connection.cursor()
        query = """
            INSERT INTO dim_employee (
                business_key,
                employee_name,
                department,
                role_name,
                salary,
                start_date,
                end_date,
                is_current
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query, rows)
        self.connection.commit()
        return len(rows)

    def load_fact_performance_reviews(self, df: pd.DataFrame) -> int:
        if df.empty:
            return 0

        self._ensure_connection()

        required = {
            "review_id",
            "employee_sk",
            "project_sk",
            "date_sk",
            "performance_score",
            "department",
            "rating",
            "review_year",
            "employee_name",
            "department_name",
            "DENSE_RANK_ANALYSIS",
        }
        missing = required.difference(df.columns)
        if missing:
            raise ValueError(f"Missing required columns for fact_performance_reviews load: {sorted(missing)}")

        rows = [
            (
                int(row["review_id"]),
                int(row["employee_sk"]),
                int(row["project_sk"]),
                int(row["date_sk"]),
                float(row["performance_score"]),
                str(row["department"]),
                str(row["rating"]),
                int(row["review_year"]),
                str(row["employee_name"]),
                str(row["department_name"]),
                int(row["DENSE_RANK_ANALYSIS"]),
            )
            for _, row in df.iterrows()
        ]

        cursor = self.connection.cursor()
        query = """
            INSERT INTO fact_performance_reviews (
                review_id,
                employee_sk,
                project_sk,
                date_sk,
                performance_score,
                department,
                rating,
                review_year,
                employee_name,
                department_name,
                DENSE_RANK_ANALYSIS
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query, rows)
        self.connection.commit()
        return len(rows)
