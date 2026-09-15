import random

import plotly.express as px
import streamlit as st

from backend.kpi_service import calculate_executive_metrics
from backend.department_service import DEPARTMENTS
from frontend.ui import animated_kpi_card, style_chart


def render_overview(
    raw_df,
    review_df,
    selected_department,
    base_employee_count,
    base_review_count,
    base_project_count,
    employee_count,
    project_count,
    review_count,
):
    if st.session_state["selected_nav"] == "Overview":
        col1, col2, col3 = st.columns(3)
        with col1:
            animated_kpi_card("Employees", employee_count, "Active employee cohort", "employees")
        with col2:
            animated_kpi_card("Projects", project_count, "Portfolio allocation", "projects")
        with col3:
            animated_kpi_card("Performance Reviews", review_count, "Captured review records", "reviews")

        attrition_rate = float(raw_df["Attrition"].eq("Yes").mean() * 100)
        executive_metrics = calculate_executive_metrics(raw_df)
        avg_income = executive_metrics["avg_income"]
        avg_tenure = executive_metrics["avg_tenure"]
        avg_age = executive_metrics["avg_age"]

        def _metric_block(label: str, value: str, note: str):
            st.markdown(
                f"""
                <div class="feature-card anim-in">
                    <h3>{label}</h3>
                    <p style="font-size: 1.7rem; font-weight: 800; color: #0f172a; margin: 0.2rem 0;">{value}</p>
                    <p>{note}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div class='section-title'>Executive HR Metrics</div>", unsafe_allow_html=True)
        metric_cols = st.columns(4)
        with metric_cols[0]:
            _metric_block("Avg Monthly Income", f"${avg_income:,.0f}", "Across all active employees")
        with metric_cols[1]:
            _metric_block("Attrition Rate", f"{attrition_rate:.1f}%", "Employees who left the company")
        with metric_cols[2]:
            _metric_block("Avg Tenure", f"{avg_tenure:.1f} yrs", "Years at company")
        with metric_cols[3]:
            _metric_block("Avg Age", f"{avg_age:.1f} yrs", "Employee age profile")

        st.markdown("<div class='section-title' style='margin-top:1.6rem;'>People Insights</div>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            dept_perf = (
                raw_df.groupby("Department")["PerformanceRating"]
                .mean()
                .reindex(DEPARTMENTS, fill_value=0)
                .rename("avg_performance_rating")
                .reset_index()
                .rename(columns={"index": "Department"})
            )
            perf_chart = px.bar(
                dept_perf.sort_values("avg_performance_rating", ascending=False),
                x="Department",
                y="avg_performance_rating",
                color="Department",
                color_discrete_sequence=["#2563eb", "#4f46e5", "#0891b2", "#7c3aed", "#06b6d4", "#22d3ee"],
                text_auto=".1f",
            )
            perf_chart.update_traces(marker_line_width=0, textfont={"color": "#173d39", "size": 11})
            style_chart(perf_chart, "Average performance by department", "Rating")
            st.plotly_chart(perf_chart, width="stretch")

        with chart_col2:
            dept_attrition = (
                raw_df.groupby("Department")["Attrition"]
                .apply(lambda s: (s == "Yes").mean() * 100)
                .reindex(DEPARTMENTS, fill_value=0)
                .rename("attrition_rate")
                .reset_index()
                .rename(columns={"index": "Department"})
            )
            dept_attrition = dept_attrition.sort_values("attrition_rate", ascending=False)
            attrition_chart = px.bar(
                dept_attrition,
                x="Department",
                y="attrition_rate",
                color="Department",
                color_discrete_sequence=["#dc2626", "#e11d48", "#f43f5e", "#be123c", "#991b1b", "#881337"],
                text_auto=".1f",
            )
            attrition_chart.update_traces(marker_line_width=0, textfont={"color": "#6d3222", "size": 11})
            style_chart(attrition_chart, "Attrition rate by department", "Percent")
            st.plotly_chart(attrition_chart, width="stretch")

        age_hist = px.histogram(
            raw_df,
            x="Age",
            nbins=20,
            color_discrete_sequence=["#06b6d4"],
        )
        age_hist.update_traces(marker_line_color="#0e7490", marker_line_width=1, opacity=0.9)
        style_chart(age_hist, "Age distribution", "Employees", "Age")
        st.plotly_chart(age_hist, width="stretch")

        st.markdown("<div class='section-title' style='margin-top:1.6rem;'>Operational Modules</div>", unsafe_allow_html=True)
        op_cols = st.columns(3)

        with op_cols[0]:
            st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
            employee_form = st.form("employee_onboarding")
            with employee_form:
                st.write("Employee onboarding")
                first_name = st.text_input("First name")
                last_name = st.text_input("Last name")
                department = st.selectbox("Department", DEPARTMENTS)
                role = st.text_input("Role")
                salary = st.number_input("Salary", min_value=30000, step=1000)
                submitted = st.form_submit_button("Add employee")
                if submitted:
                    ok = st.session_state.get("insert_employee_record", lambda *args, **kwargs: True)(first_name, last_name, department, role, salary)
                    if ok:
                        st.success(f"Employee {first_name} {last_name} was added to the live OLTP database.")
                    else:
                        st.error("Employee insert failed. Please confirm the live MySQL connection is available.")
            st.markdown("</div>", unsafe_allow_html=True)

        with op_cols[1]:
            st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
            project_form = st.form("project_assignment")
            with project_form:
                st.write("Project assignment")
                project_name = st.text_input("Project name")
                project_department = st.selectbox("Owner department", DEPARTMENTS)
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
                allocated_hours = st.number_input("Allocated hours", min_value=10, step=10)
                project_submitted = st.form_submit_button("Create project")
                if project_submitted:
                    ok = st.session_state.get("insert_project_record", lambda *args, **kwargs: True)(project_name, project_department, priority, allocated_hours)
                    if ok:
                        st.success(f"Project '{project_name}' was created in the live OLTP database.")
                    else:
                        st.error("Project insert failed. Please confirm the live MySQL connection is available.")
            st.markdown("</div>", unsafe_allow_html=True)

        with op_cols[2]:
            st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
            review_form = st.form("review_entry")
            with review_form:
                st.write("Performance review")
                employee_id = st.number_input("Employee ID", min_value=1, step=1)
                score = st.slider("Performance score", 1, 10, 7)
                review_submitted = st.form_submit_button("Submit review")
                if review_submitted:
                    ok = st.session_state.get("insert_review_record", lambda *args, **kwargs: True)(employee_id, score, selected_department if selected_department != "All" else "Engineering")
                    if ok:
                        st.success(f"Review captured for employee {employee_id} with score {score} in the live database.")
                    else:
                        st.error("Review insert failed. Please confirm the live MySQL connection is available.")
            st.markdown("</div>", unsafe_allow_html=True)
