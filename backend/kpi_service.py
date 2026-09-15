import pandas as pd


def calculate_executive_metrics(raw_df: pd.DataFrame) -> dict[str, float]:
    """Calculate the executive HR metrics used by the dashboard."""
    attrition_rate = float(raw_df["Attrition"].eq("Yes").mean() * 100)

    def series_value(column: str) -> float:
        series = raw_df[column]
        if isinstance(series, pd.DataFrame):
            series = series.iloc[:, 0]
        return float(pd.to_numeric(series, errors="coerce").mean())

    return {
        "attrition_rate": attrition_rate,
        "avg_income": series_value("MonthlyIncome"),
        "avg_tenure": series_value("YearsAtCompany"),
        "avg_age": series_value("Age"),
    }


def calculate_kpi_counts(history_df: pd.DataFrame, review_df: pd.DataFrame):
    """Calculate the base KPI counts."""
    return {
        "employees": history_df["employee_id"].nunique(),
        "projects": 250,
        "reviews": len(review_df),
    }
