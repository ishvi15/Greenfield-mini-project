import plotly.express as px
import streamlit as st

from backend.analytics_service import build_warehouse_analytics
from backend.department_service import DEPARTMENTS
from frontend.ui import style_chart


def render_warehouse_analytics(warehouse_review_df, selected_department, selected_year):
    filtered_reviews = warehouse_review_df.copy()
    if not st.session_state.get("warehouse_ready", False):
        st.error("Warehouse analytics is unavailable. Load hr_analytics_warehouse first.")
    if selected_department != "All":
        filtered_reviews = filtered_reviews[filtered_reviews["department"] == selected_department]
    if selected_year != "All":
        filtered_reviews = filtered_reviews[filtered_reviews["review_date"].str.startswith(str(selected_year))]

    if filtered_reviews.empty:
        st.info("No warehouse data matches the selected filters.")
        return

    performance_df, ranked_df, risk_df = build_warehouse_analytics(filtered_reviews)

    st.markdown("<div class='section-title' style='margin-top:1.8rem;'>Warehouse Analytics</div>", unsafe_allow_html=True)
    analytics_tab = st.tabs(["Performance Trends", "Top Employees", "Attrition Risk"])

    with analytics_tab[0]:
        if performance_df.empty:
            st.info("No performance records match the selected filter.")
        else:
            performance_df["year"] = performance_df["year"].astype(str)
            perf_fig = px.bar(
                performance_df,
                x="year",
                y="avg_score",
                text_auto=".1f",
                color_discrete_sequence=["#2563eb"],
            )
            perf_fig.update_traces(
                marker_line_width=0,
                textfont={"color": "#173d39", "size": 11},
            )
            style_chart(perf_fig, "Average performance by year", "Average score", "Year")
            st.plotly_chart(perf_fig, width="stretch")

    with analytics_tab[1]:
        if ranked_df.empty:
            st.info("No employee rankings match the selected filter.")
        else:
            top_employees = ranked_df[ranked_df["department_rank"] <= 5].copy()
            top_employees = top_employees[["department", "employee_id", "performance_score", "department_rank"]]
            st.dataframe(top_employees, width="stretch")

    with analytics_tab[2]:
        if risk_df.empty:
            st.info("No attrition risk data is available for the selected filter.")
        else:
            if selected_department == "All":
                risk_df = (
                    risk_df.set_index("department")
                    .reindex(DEPARTMENTS, fill_value=0)
                    .rename_axis("department")
                    .reset_index()
                )
            risk_fig = px.bar(
                risk_df,
                x="department",
                y="risk_score",
                color="department",
                color_discrete_sequence=["#dc2626", "#e11d48", "#f43f5e", "#be123c", "#991b1b", "#881337"],
                text_auto=".1f",
            )
            risk_fig.update_traces(marker_line_width=0, textfont={"color": "#6d3222", "size": 11})
            style_chart(risk_fig, "Attrition risk by department", "Risk score")
            st.plotly_chart(risk_fig, width="stretch")
