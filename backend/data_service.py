import os
from pathlib import Path

import pandas as pd
import streamlit as st

from src.hr_analytics.db_manager import DatabaseConnection


def _resolve_project_data_file(*candidates: str) -> Path:
    """Return the first dataset path that exists across both legacy and current layouts."""
    project_root = Path(__file__).resolve().parents[1]
    for candidate in candidates:
        path = project_root / candidate
        if path.exists():
            return path

        direct_path = Path(candidate)
        if direct_path.exists():
            return direct_path

    return project_root / candidates[0]


def _warehouse_database(cursor, connection) -> str:
    configured = os.getenv("MYSQL_WAREHOUSE_DATABASE", "").strip().strip('"').strip("'")
    connected = getattr(connection, "database", "") or ""
    candidates = [configured, connected, "hr_db", "defaultdb", "hr_analytics_warehouse"]
    cursor.execute("SHOW DATABASES")
    database_rows = cursor.fetchall()
    available = {
        next(iter(row.values())) if isinstance(row, dict) else row[0]
        for row in database_rows
    }
    for database in dict.fromkeys(candidates):
        if database in available:
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = %s
                  AND table_name IN ('fact_performance_reviews', 'dim_employee', 'dim_date')
                """,
                (database,),
            )
            table_count = cursor.fetchone()
            table_count = next(iter(table_count.values())) if isinstance(table_count, dict) else table_count[0]
            if table_count == 3:
                return database
    raise ValueError("No database with the required warehouse tables was found.")


@st.cache_data(show_spinner="Loading HR analytics data...")
def ensure_demo_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load and transform the bundled IBM HR dataset for demo/fallback use."""
    raw_path = _resolve_project_data_file(
        "data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "data/raw_data/WA_Fn-UseC_-HR-Employee-Attrition.csv",
        "data/WA_Fn-UseC_-HR-Employee-Attrition.csv",
    )
    if not raw_path.exists():
        raise FileNotFoundError(f"Required IBM HR file not found. Checked: {raw_path}")

    raw_df = pd.read_csv(raw_path)
    required = {
        "EmployeeNumber", "Department", "YearsAtCompany",
        "PerformanceRating", "MonthlyIncome", "Attrition", "Age"
    }
    missing = required - set(raw_df.columns)
    if missing:
        # Handle the moved synthesized dataset format as a compatibility fallback.
        processed_path = _resolve_project_data_file(
            "data/processed/employee_synthesized.csv",
            "data/employee_synthesized.csv",
        )
        if not processed_path.exists():
            raise ValueError(
                f"IBM HR dataset is missing required columns: {sorted(missing)}"
            )

        raw_df = pd.read_csv(processed_path)
        required = {"EmployeeNumber", "Department", "PerformanceRating", "MonthlyIncome", "Attrition", "Age"}
        missing = required - set(raw_df.columns)
        if missing:
            raise ValueError(
                f"Processed employee dataset is missing required columns: {sorted(missing)}"
            )

    if "EmployeeNumber" not in raw_df.columns and "EmployeeID" in raw_df.columns:
        raw_df = raw_df.rename(columns={"EmployeeID": "EmployeeNumber"})

    if "YearsAtCompany" not in raw_df.columns and "YearsAtCompany" not in raw_df.columns:
        if "YearsAtCompany" in raw_df.columns:
            pass

    if "YearsAtCompany" not in raw_df.columns:
        if "HireDate" in raw_df.columns:
            raw_df["YearsAtCompany"] = (
                (pd.Timestamp.now().normalize() - pd.to_datetime(raw_df["HireDate"])) / pd.Timedelta(days=365)
            ).round(1)
        else:
            raw_df["YearsAtCompany"] = 0

    history_df = raw_df[
        ["EmployeeNumber", "Department", "YearsAtCompany", "PerformanceRating"]
    ].copy()
    history_df = history_df.rename(
        columns={
            "EmployeeNumber": "employee_id",
            "Department": "department",
            "YearsAtCompany": "years_at_company",
            "PerformanceRating": "performance_score",
        }
    )
    history_df["review_date"] = pd.to_datetime(
        2024 - history_df["years_at_company"].astype(int), format="%Y"
    )
    history_df["review_date"] = history_df["review_date"].apply(
        lambda d: d.strftime("%Y-%m-%d")
    )
    history_df = history_df[
        ["employee_id", "department", "review_date", "performance_score"]
    ]

    review_df = history_df.copy()
    review_df["review_id"] = range(1, len(review_df) + 1)
    review_df = review_df[
        ["review_id", "employee_id", "review_date", "performance_score", "department"]
    ]
    return history_df, review_df, raw_df


@st.cache_data(show_spinner="Loading live HR analytics data...")
def load_live_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load review and employee data from MySQL."""
    conn = DatabaseConnection().get_connection()
    cursor = conn.cursor(dictionary=True)
    database = _warehouse_database(cursor, conn)

    cursor.execute(
        """
        SELECT employee_id, department, review_date, performance_score
        FROM hr_analytics_oltp.reviews
        ORDER BY review_date ASC
        """
    )
    review_rows = cursor.fetchall()
    if not review_rows:
        cursor.execute(
            f"""
            SELECT
                fact.review_id,
                employee.business_key AS employee_id,
                employee.department,
                date_dim.full_date AS review_date,
                fact.performance_score
            FROM `{database}`.fact_performance_reviews AS fact
            JOIN `{database}`.dim_employee AS employee
                ON employee.employee_sk = fact.employee_sk
            JOIN `{database}`.dim_date AS date_dim
                ON date_dim.date_sk = fact.date_sk
            ORDER BY date_dim.full_date ASC, fact.review_id ASC
            """
        )
        review_rows = cursor.fetchall()
    review_df = pd.DataFrame(review_rows)
    if review_df.empty:
        raise ValueError("No review rows found in the live MySQL database.")

    review_df["review_date"] = pd.to_datetime(
        review_df["review_date"]
    ).dt.strftime("%Y-%m-%d")
    history_df = review_df[
        ["employee_id", "department", "review_date", "performance_score"]
    ].copy()
    review_df = review_df.copy()
    if "review_id" not in review_df.columns:
        review_df.insert(0, "review_id", range(1, len(review_df) + 1))

    cursor.execute(
        f"""
        SELECT employee_id, department, role_name, salary, hire_date
        FROM hr_analytics_oltp.employees
        """
    )
    employee_df = pd.DataFrame(cursor.fetchall())
    if employee_df.empty:
        cursor.execute(
            f"""
            SELECT
                business_key AS employee_id,
                department,
                role_name,
                salary,
                start_date AS hire_date
            FROM `{database}`.dim_employee
            WHERE is_current = 1
            """
        )
        employee_df = pd.DataFrame(cursor.fetchall())

    raw_df = employee_df[
        ["employee_id", "department", "role_name", "salary", "hire_date"]
    ].copy()
    raw_df["PerformanceRating"] = pd.to_numeric(
        review_df["performance_score"].head(len(raw_df)), errors="coerce"
    ).fillna(70)
    raw_df["YearsAtCompany"] = (
        (
            pd.Timestamp.now().normalize()
            - pd.to_datetime(raw_df["hire_date"])
        ) / pd.Timedelta(days=365)
    ).round(1)
    raw_df["Attrition"] = "No"
    raw_df["Age"] = 35
    raw_df["MonthlyIncome"] = pd.to_numeric(
        raw_df["salary"], errors="coerce"
    ).fillna(0)
    raw_df = raw_df.rename(
        columns={"employee_id": "EmployeeNumber", "department": "Department"}
    )
    raw_df = raw_df[
        [
            "EmployeeNumber", "Department", "YearsAtCompany",
            "PerformanceRating", "MonthlyIncome", "Attrition", "Age"
        ]
    ]
    return history_df, review_df, raw_df


@st.cache_data(show_spinner="Loading warehouse analytics...")
def load_warehouse_analytics_data() -> pd.DataFrame:
    """Load analytics rows from the reporting warehouse, not the OLTP database."""
    conn = DatabaseConnection().get_connection()
    cursor = conn.cursor(dictionary=True)
    warehouse_database = _warehouse_database(cursor, conn)
    cursor.execute(
        f"""
        SELECT
            fact.review_id,
            employee.business_key AS employee_id,
            employee.department,
            date_dim.full_date AS review_date,
            fact.performance_score
        FROM `{warehouse_database}`.fact_performance_reviews AS fact
        JOIN `{warehouse_database}`.dim_employee AS employee
            ON employee.employee_sk = fact.employee_sk
        JOIN `{warehouse_database}`.dim_date AS date_dim
            ON date_dim.date_sk = fact.date_sk
        ORDER BY date_dim.full_date ASC, fact.review_id ASC
        """
    )
    rows = cursor.fetchall()
    warehouse_df = pd.DataFrame(rows)
    if warehouse_df.empty:
        raise ValueError(f"No warehouse fact rows found in {warehouse_database}.")
    warehouse_df["review_date"] = pd.to_datetime(warehouse_df["review_date"]).dt.strftime("%Y-%m-%d")
    return warehouse_df[
        ["review_id", "employee_id", "department", "review_date", "performance_score"]
    ]


def load_hr_data():
    """Prefer live MySQL data and fall back to the bundled demo dataset."""
    try:
        history_df, review_df, raw_df = load_live_data()
        db_ready = bool(os.getenv("MYSQL_HOST")) and not history_df.empty
        return history_df, review_df, raw_df, db_ready
    except Exception:
        history_df, review_df, raw_df = ensure_demo_data()
        return history_df, review_df, raw_df, False
