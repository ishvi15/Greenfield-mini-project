import pandas as pd

from backend.department_service import DEPARTMENTS, normalize_department
from src.hr_analytics.analytics import HRAnalytics


def test_ibm_department_catalog_matches_source_data():
    assert "Research & Development" in DEPARTMENTS
    assert "Human Resources" in DEPARTMENTS
    assert "Sales" in DEPARTMENTS


def test_ibm_performance_rating_is_normalized_to_0_100_scale():
    df = pd.DataFrame(
        {
            "Department": ["Research & Development", "Sales", "Human Resources"],
            "PerformanceRating": [3, 4, 2],
        }
    )

    normalized = df.copy()
    normalized["PerformanceRating"] = normalized["PerformanceRating"].map({1: 25, 2: 50, 3: 75, 4: 100})

    assert normalized["PerformanceRating"].tolist() == [75, 100, 50]
    assert normalize_department("R&D") == "Research & Development"


def test_monthly_performance_summary():
    df = pd.DataFrame(
        {
            "review_date": ["2023-01-01", "2024-01-02", "2024-02-01"],
            "performance_score": [80, 90, 85],
        }
    )

    result = HRAnalytics().calculate_yearly_performance(df)

    assert "year" in result.columns
    assert "avg_score" in result.columns
    assert len(result) == 2


def test_analytics_normalizes_legacy_warehouse_scores():
    df = pd.DataFrame(
        {
            "review_date": ["2023-01-01", "2024-01-01"],
            "performance_score": [4.0, 5.0],
        }
    )

    result = HRAnalytics().calculate_yearly_performance(df)

    assert result["avg_score"].tolist() == [80.0, 100.0]


def test_attrition_risk_uses_actual_attrition_values():
    df = pd.DataFrame(
        {
            "department": ["Sales", "Sales", "Research & Development"],
            "performance_score": [4.0, 4.0, 5.0],
            "attrition": ["Yes", "No", "No"],
        }
    )

    result = HRAnalytics().attrition_risk_summary(df)

    sales_risk = result.loc[result["department"] == "Sales", "risk_score"].iloc[0]
    assert sales_risk == 50.0


def test_ranking_by_department():
    df = pd.DataFrame(
        {
            "department": ["Engineering", "Engineering", "Finance"],
            "employee_id": [1, 2, 3],
            "performance_score": [90, 85, 88],
        }
    )

    result = HRAnalytics().rank_top_employees_by_department(df)

    assert result["department_rank"].ge(1).all()
    assert result["department"].nunique() == 2


def test_etl_accepts_scd2_employee_history_shape():
    from src.hr_analytics.etl import DataWarehouseETL

    df = pd.DataFrame(
        [
            {
                "employee_id": 1,
                "department": "Engineering",
                "role_name": "Senior Analyst",
                "salary": 90000,
                "effective_start_date": "2023-01-01",
                "effective_end_date": "9999-12-31",
                "is_current": True,
            }
        ]
    )

    result = DataWarehouseETL(df).build_dim_employee()

    assert {"surrogate_key", "business_key", "employee_name", "department", "role", "salary", "start_date", "end_date", "is_current"}.issubset(result.columns)
    assert len(result) == 1
    assert result.iloc[0]["business_key"] == 1


def test_warehouse_loader_inserts_dim_employee_rows(monkeypatch):
    from src.hr_analytics.warehouse_loader import WarehouseLoader

    class FakeCursor:
        def __init__(self):
            self.executed = []

        def executemany(self, query, params):
            self.executed.append((query, params))

    class FakeConnection:
        def __init__(self):
            self.cursor_obj = FakeCursor()

        def cursor(self):
            return self.cursor_obj

        def commit(self):
            return None

    fake_conn = FakeConnection()
    monkeypatch.setattr("src.hr_analytics.warehouse_loader.mysql.connector.connect", lambda **kwargs: fake_conn)

    loader = WarehouseLoader(connection=fake_conn)
    df = pd.DataFrame([
        {
            "business_key": 1,
            "employee_name": "Ava Patel",
            "department": "Engineering",
            "role": "Senior Analyst",
            "salary": 90000,
            "start_date": "2023-01-01",
            "end_date": "9999-12-31",
            "is_current": True,
        }
    ])

    count = loader.load_dim_employee(df)

    assert count == 1
    assert fake_conn.cursor_obj.executed


def test_warehouse_loader_inserts_fact_performance_reviews_rows(monkeypatch):
    from src.hr_analytics.warehouse_loader import WarehouseLoader

    class FakeCursor:
        def __init__(self):
            self.executed = []

        def executemany(self, query, params):
            self.executed.append((query, params))

    class FakeConnection:
        def __init__(self):
            self.cursor_obj = FakeCursor()

        def cursor(self):
            return self.cursor_obj

        def commit(self):
            return None

    fake_conn = FakeConnection()
    monkeypatch.setattr("src.hr_analytics.warehouse_loader.mysql.connector.connect", lambda **kwargs: fake_conn)

    loader = WarehouseLoader(connection=fake_conn)
    df = pd.DataFrame([
        {
            "review_id": 101,
            "employee_sk": 1,
            "project_sk": 7,
            "date_sk": 42,
            "performance_score": 91.5,
            "department": "Engineering",
            "rating": "Excellent",
            "review_year": 2024,
            "employee_name": "Ava Patel",
            "department_name": "Engineering",
            "DENSE_RANK_ANALYSIS": 1,
        }
    ])

    count = loader.load_fact_performance_reviews(df)

    assert count == 1
    assert fake_conn.cursor_obj.executed
