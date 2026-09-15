from __future__ import annotations

from typing import Any

import pandas as pd


class HRAnalytics:
    def calculate_yearly_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["year", "avg_score"])

        if "review_date" not in df.columns or "performance_score" not in df.columns:
            raise ValueError("DataFrame must include review_date and performance_score columns.")

        df = df.copy()
        df["review_date"] = pd.to_datetime(df["review_date"])
        df["year"] = df["review_date"].dt.year
        summary = df.groupby("year", as_index=False)["performance_score"].mean()
        summary = summary.rename(columns={"performance_score": "avg_score"})
        return summary.sort_values("year").reset_index(drop=True)

    def rank_top_employees_by_department(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["department", "employee_id", "performance_score", "department_rank"])

        required = {"department", "employee_id", "performance_score"}
        if not required.issubset(df.columns):
            raise ValueError("DataFrame must include department, employee_id, and performance_score columns.")

        ranked = df.copy()
        ranked["department_rank"] = (
            ranked.groupby("department")["performance_score"]
            .rank(method="dense", ascending=False)
            .astype(int)
        )
        return ranked.sort_values(["department", "department_rank"]).reset_index(drop=True)

    def attrition_risk_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["department", "risk_score"])

        if not {"department", "performance_score"}.issubset(df.columns):
            raise ValueError("DataFrame must include department and performance_score columns.")

        summary = df.groupby("department", as_index=False)["performance_score"].mean()
        summary["risk_score"] = 100 - summary["performance_score"]
        return summary.sort_values("risk_score", ascending=False).reset_index(drop=True)
