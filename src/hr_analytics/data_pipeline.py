from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data_synthesizer import EmployeeHistorySynthesizer


class EmployeeDataPipeline:
    def __init__(self, output_dir: str | Path = "data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_ibm_attrition_data(self, raw_csv_path: str | Path) -> pd.DataFrame:
        source_path = Path(raw_csv_path)
        if not source_path.exists():
            raise FileNotFoundError(f"IBM dataset not found: {source_path}")

        df = pd.read_csv(source_path)
        if "EmployeeNumber" not in df.columns:
            raise ValueError(f"Expected EmployeeNumber column in IBM file: {source_path}")

        cleaned = df.copy()
        cleaned["employee_id"] = cleaned["EmployeeNumber"].astype(int)
        cleaned["department"] = cleaned["Department"].fillna("Unknown")

        if "PerformanceRating" in cleaned.columns:
            performance_scores = pd.to_numeric(cleaned["PerformanceRating"], errors="coerce")
        elif "JobSatisfaction" in cleaned.columns:
            performance_scores = pd.to_numeric(cleaned["JobSatisfaction"], errors="coerce") * 20
        else:
            monthly_income = pd.to_numeric(cleaned.get("MonthlyIncome", 0), errors="coerce")
            performance_scores = monthly_income / 1500

        cleaned["performance_score"] = performance_scores.fillna(70).clip(0, 100)

        if "YearsAtCompany" in cleaned.columns:
            years_at_company = pd.to_numeric(cleaned["YearsAtCompany"], errors="coerce").fillna(0)
            review_years = 2024 - years_at_company.astype(int)
            review_years = review_years.clip(2015, 2024)
            cleaned["review_date"] = pd.to_datetime(review_years.astype(str) + "-01-01")
        else:
            cleaned["review_date"] = pd.Timestamp("2024-01-01")

        history_df = cleaned[["employee_id", "department", "review_date", "performance_score"]].copy()

        output_history = self.output_dir / "employee_history_stage.csv"
        history_df.to_csv(output_history, index=False)
        return history_df

    def generate_scd2_employee_history(self, raw_csv_path: str | Path, total_employees: int | None = None) -> pd.DataFrame:
        synthesizer = EmployeeHistorySynthesizer(source_path=raw_csv_path)
        history_df = synthesizer.generate_scd2_employee_history(total_employees=total_employees)
        output_path = self.output_dir / "employee_scd2_history.csv"
        history_df.to_csv(output_path, index=False)
        return history_df

    def generate_ibm_review_dataset(self, employee_history_df: pd.DataFrame) -> pd.DataFrame:
        if employee_history_df.empty:
            return pd.DataFrame(columns=["review_id", "employee_id", "review_date", "performance_score", "department"])

        review_rows = []
        for idx, row in employee_history_df.iterrows():
            review_rows.append(
                {
                    "review_id": idx + 1,
                    "employee_id": int(row["employee_id"]),
                    "review_date": pd.to_datetime(row["review_date"]).strftime("%Y-%m-%d"),
                    "performance_score": float(row["performance_score"]),
                    "department": row["department"],
                }
            )

        review_df = pd.DataFrame(review_rows)
        output_path = self.output_dir / "performance_reviews.csv"
        review_df.to_csv(output_path, index=False)
        return review_df
