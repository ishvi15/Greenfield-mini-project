from __future__ import annotations

from typing import Any

import pandas as pd


class HRAnalytics:
    @staticmethod
    def _normalize_scores(values: pd.Series) -> pd.Series:
        scores = pd.to_numeric(values, errors="coerce")
        maximum = scores.max()
        if pd.notna(maximum) and maximum <= 4:
            return scores / 4 * 100
        if pd.notna(maximum) and maximum <= 5:
            return scores / 5 * 100
        return scores.clip(0, 100)

    def calculate_yearly_performance(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return pd.DataFrame(columns=["year", "avg_score"])

        if "review_date" not in df.columns or "performance_score" not in df.columns:
            raise ValueError("DataFrame must include review_date and performance_score columns.")

        df = df.copy()
        df["review_date"] = pd.to_datetime(df["review_date"])
        df["performance_score"] = self._normalize_scores(df["performance_score"])
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
        ranked["performance_score"] = self._normalize_scores(ranked["performance_score"])
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

        normalized = df.copy()
        normalized["performance_score"] = self._normalize_scores(normalized["performance_score"])
        if "attrition" in normalized.columns:
            normalized["attrition"] = normalized["attrition"].astype(str).str.strip().str.casefold()
            summary = (
                normalized.assign(attrition_rate=normalized["attrition"].eq("yes").astype(float) * 100)
                .groupby("department", as_index=False)["attrition_rate"]
                .mean()
                .rename(columns={"attrition_rate": "risk_score"})
            )
        else:
            summary = normalized.groupby("department", as_index=False)["performance_score"].mean()
            summary["risk_score"] = 100 - summary["performance_score"]
        return summary.sort_values("risk_score", ascending=False).reset_index(drop=True)
