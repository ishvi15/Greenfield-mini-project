from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

import pandas as pd


class DataWarehouseETL:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe.copy()

    def normalize_employee_history(self) -> pd.DataFrame:
        preferred = {
            "employee_id",
            "employee_name",
            "department",
            "salary",
            "role",
            "start_date",
            "end_date",
            "is_current",
        }
        alternative = {
            "employee_id",
            "department",
            "role_name",
            "salary",
            "effective_start_date",
            "effective_end_date",
            "is_current",
        }

        columns = set(self.dataframe.columns)
        if preferred.issubset(columns):
            df = self.dataframe.copy()
            df = df.rename(columns={"employee_name": "employee_name", "role": "role", "start_date": "start_date", "end_date": "end_date"})
        elif alternative.issubset(columns):
            df = self.dataframe.copy()
            df["employee_name"] = df.get("employee_name", df["employee_id"].astype(str))
            df["role"] = df["role_name"]
            df["start_date"] = df["effective_start_date"]
            df["end_date"] = df["effective_end_date"]
        else:
            missing = preferred.difference(columns) - {"employee_name", "role", "start_date", "end_date"}
            if not missing:
                missing = preferred.difference(columns)
            raise ValueError(f"Missing required columns for SCD history: {sorted(missing)}")

        df["start_date"] = pd.to_datetime(df["start_date"])
        df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce").fillna(pd.Timestamp("9999-12-31"))
        df["salary"] = pd.to_numeric(df["salary"], errors="coerce").fillna(0).astype(float)
        df["is_current"] = df["is_current"].astype(bool)
        return df.sort_values(["employee_id", "start_date"]).reset_index(drop=True)

    def build_dim_employee(self) -> pd.DataFrame:
        df = self.normalize_employee_history()
        dim = df[["employee_id", "employee_name", "department", "role", "salary", "start_date", "end_date", "is_current"]].copy()
        dim.insert(0, "surrogate_key", range(1, len(dim) + 1))
        dim.rename(columns={"employee_id": "business_key"}, inplace=True)
        return dim

    def build_fact_performance_reviews(self, review_rows: Iterable[dict]) -> pd.DataFrame:
        rows = list(review_rows)
        if not rows:
            return pd.DataFrame(columns=["review_id", "employee_key", "project_key", "date_key", "performance_score", "rating"])

        fact = pd.DataFrame(rows)
        fact["review_date"] = pd.to_datetime(fact["review_date"])
        fact["review_year"] = fact["review_date"].dt.year
        fact["rating"] = fact["performance_score"].apply(lambda value: "Excellent" if value >= 90 else "Good" if value >= 75 else "Needs Improvement")
        return fact

    def generate_demo_reviews(self, total_rows: int = 1000) -> pd.DataFrame:
        rng = pd.date_range(start="2020-01-01", periods=total_rows, freq="D")
        records = []
        for idx, date_value in enumerate(rng, start=1):
            records.append(
                {
                    "review_id": idx,
                    "employee_key": (idx % 500) + 1,
                    "project_key": (idx % 25) + 1,
                    "review_date": date_value,
                    "performance_score": round(float((idx % 40) + 60 + (idx % 7) * 2.5), 2),
                    "rating": "Excellent" if (idx % 5) == 0 else "Good",
                }
            )
        return pd.DataFrame(records)
