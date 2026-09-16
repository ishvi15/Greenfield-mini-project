from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class EmployeeHistorySynthesizer:
    """Build a project-ready HR history dataset from the raw IBM attrition CSV."""

    source_path: str | Path = "data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv"

    def _resolve_source_path(self) -> Path:
        project_root = Path(__file__).resolve().parents[2]
        requested = Path(self.source_path)
        candidates = [requested]
        if not requested.is_absolute():
            candidates.extend([
                project_root / requested,
                project_root / "data/raw" / requested.name,
                project_root / "data/raw_data" / requested.name,
            ])
        for candidate in candidates:
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"IBM HR dataset not found. Checked: {candidates}")

    def load_raw_data(self) -> pd.DataFrame:
        path = self._resolve_source_path()
        df = pd.read_csv(path)
        required = {"EmployeeNumber", "Department", "YearsAtCompany", "PerformanceRating"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"IBM HR dataset is missing required columns: {sorted(missing)}")
        return df

    def generate_employee_history(self, total_employees: int | None = None, years: int = 5) -> pd.DataFrame:
        raw_df = self.load_raw_data()

        if total_employees is not None:
            raw_df = raw_df.head(total_employees)

        history_df = raw_df[["EmployeeNumber", "Department", "YearsAtCompany", "PerformanceRating"]].copy()
        history_df = history_df.rename(columns={
            "EmployeeNumber": "employee_id",
            "Department": "department",
            "YearsAtCompany": "years_at_company",
            "PerformanceRating": "performance_score",
        })

        years_at_company = pd.to_numeric(history_df["years_at_company"], errors="coerce").fillna(0).astype(int)
        review_years = 2024 - years_at_company
        review_years = review_years.clip(2015, 2024)
        history_df["review_date"] = pd.to_datetime(review_years.astype(str) + "-01-01")
        history_df["review_date"] = history_df["review_date"].dt.strftime("%Y-%m-%d")

        history_df = history_df[["employee_id", "department", "review_date", "performance_score"]].copy()
        history_df = history_df.sort_values(["employee_id", "review_date"]).reset_index(drop=True)
        return history_df

    def generate_scd2_employee_history(self, total_employees: int | None = None) -> pd.DataFrame:
        raw_df = self.load_raw_data()
        if total_employees is not None:
            raw_df = raw_df.head(total_employees)

        df = raw_df[["EmployeeNumber", "Department", "YearsAtCompany", "PerformanceRating", "MonthlyIncome", "JobRole"]].copy()
        df = df.rename(columns={
            "EmployeeNumber": "employee_id",
            "Department": "department",
            "YearsAtCompany": "years_at_company",
            "PerformanceRating": "performance_score",
            "MonthlyIncome": "salary",
            "JobRole": "role_name",
        })

        df["salary"] = pd.to_numeric(df["salary"], errors="coerce").fillna(50000)
        df["role_name"] = df["role_name"].fillna("Analyst")
        df["department"] = df["department"].fillna("Unknown")

        rows = []
        for _, row in df.iterrows():
            employee_id = int(row["employee_id"])
            current_date = pd.Timestamp("2024-01-01")
            start_date = current_date - pd.DateOffset(years=max(1, int(row["years_at_company"])))
            end_date = current_date + pd.DateOffset(years=1)
            rows.append(
                {
                    "employee_id": employee_id,
                    "department": row["department"],
                    "role_name": row["role_name"],
                    "salary": float(row["salary"]),
                    "effective_start_date": start_date.strftime("%Y-%m-%d"),
                    "effective_end_date": end_date.strftime("%Y-%m-%d"),
                    "is_current": True,
                }
            )

        history_df = pd.DataFrame(rows)
        history_df = history_df.sort_values(["employee_id", "effective_start_date"]).reset_index(drop=True)
        return history_df

    def generate_review_dataset(self, total_reviews: int | None = None) -> pd.DataFrame:
        history_df = self.generate_employee_history(total_employees=total_reviews)
        review_df = history_df.copy()
        review_df["review_id"] = range(1, len(review_df) + 1)
        review_df = review_df[["review_id", "employee_id", "review_date", "performance_score", "department"]]
        return review_df
