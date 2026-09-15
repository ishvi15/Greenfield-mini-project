import pandas as pd

from src.hr_analytics.analytics import HRAnalytics


def build_warehouse_analytics(filtered_reviews: pd.DataFrame):
    """Build performance, ranking, and attrition-risk datasets."""
    if filtered_reviews.empty:
        return (
            pd.DataFrame(columns=["year", "avg_score"]),
            pd.DataFrame(
                columns=[
                    "department", "employee_id",
                    "performance_score", "department_rank"
                ]
            ),
            pd.DataFrame(columns=["department", "risk_score"]),
        )

    analytics = HRAnalytics()
    return (
        analytics.calculate_yearly_performance(filtered_reviews),
        analytics.rank_top_employees_by_department(filtered_reviews),
        analytics.attrition_risk_summary(filtered_reviews),
    )
