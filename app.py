import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

from backend.analytics_service import build_warehouse_analytics
from backend.data_service import ensure_demo_data, load_live_data, load_warehouse_analytics_data
from backend.db_service import (
    get_last_insert_error,
    insert_employee_record,
    insert_project_record,
    insert_review_record,
)
from frontend.pages.employee_onboarding import render_employee_onboarding
from frontend.pages.overview import render_overview
from frontend.pages.project_assignment import render_project_assignment
from frontend.pages.review_tracking import render_review_tracking
from frontend.pages.warehouse_analytics import render_warehouse_analytics
from frontend.styles import CUSTOM_CSS
from frontend.ui import get_dashboard_counts, render_hero, render_sidebar

load_dotenv()


st.set_page_config(page_title="HR Analytics Command Center", layout="wide")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

flash_message = st.session_state.pop("flash_message", None)
if flash_message:
    st.success(flash_message)

if "db_ready" not in st.session_state:
    st.session_state["db_ready"] = False
if "kpi_history" not in st.session_state:
    # rolling sparkline history per metric, seeded on first load
    st.session_state["kpi_history"] = {"employees": [], "projects": [], "reviews": []}
if "kpi_prev" not in st.session_state:
    st.session_state["kpi_prev"] = {"employees": 0, "projects": 250, "reviews": 0}

try:
    history_df, review_df, raw_df = load_live_data()
    st.session_state["db_ready"] = bool(os.getenv("MYSQL_HOST")) and not history_df.empty
except Exception:
    history_df, review_df, raw_df = ensure_demo_data()
    st.session_state["db_ready"] = False

try:
    warehouse_review_df = load_warehouse_analytics_data()
    st.session_state["warehouse_ready"] = True
except Exception:
    warehouse_review_df = pd.DataFrame(
        columns=["review_id", "employee_id", "department", "review_date", "performance_score"]
    )
    st.session_state["warehouse_ready"] = False







selected_department, selected_year = render_sidebar(history_df, review_df, warehouse_review_df)

hero_counts = get_dashboard_counts(raw_df, review_df, history_df)
hero_team_count = hero_counts["teams"]
hero_project_count = hero_counts["projects"]
hero_review_count = hero_counts["reviews"]

render_hero(hero_team_count, hero_project_count, hero_review_count)

base_employee_count = history_df["employee_id"].nunique()
base_review_count = len(review_df)
base_project_count = hero_project_count or 250
employee_count, project_count, review_count = base_employee_count, base_project_count, base_review_count

if st.session_state["selected_nav"] == "Overview":
    render_overview(
        raw_df,
        review_df,
        selected_department,
        base_employee_count,
        base_review_count,
        base_project_count,
        employee_count,
        project_count,
        review_count,
    )
elif st.session_state["selected_nav"] == "Employee Onboarding":
    render_employee_onboarding()
elif st.session_state["selected_nav"] == "Project Assignment":
    render_project_assignment()
elif st.session_state["selected_nav"] == "Review Tracking":
    render_review_tracking()
elif st.session_state["selected_nav"] == "Warehouse Analytics":
    render_warehouse_analytics(warehouse_review_df, selected_department, selected_year)

