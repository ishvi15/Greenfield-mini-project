import streamlit as st

from backend.db_service import get_last_insert_error, insert_project_assignment
from backend.data_service import load_live_data
from backend.department_service import DEPARTMENTS


def render_project_assignment():
    st.markdown("<div class='section-title'>Project Assignment</div>", unsafe_allow_html=True)
    st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
    project_form = st.form("project_assignment_only")
    with project_form:
        st.write("Project assignment")
        project_name = st.text_input("Project name")
        employee_id = st.number_input("Employee ID to assign", min_value=1, step=1)
        project_department = st.selectbox("Owner department", DEPARTMENTS)
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        allocated_hours = st.number_input("Allocated hours", min_value=10, step=10)
        project_submitted = st.form_submit_button("Create project")
        if project_submitted:
            if insert_project_assignment(project_name, project_department, priority, allocated_hours, employee_id):
                load_live_data.clear()
                st.session_state["flash_message"] = f"Project '{project_name}' created and assigned to employee {employee_id}."
                st.rerun()
            else:
                st.error(get_last_insert_error() or "Project assignment could not be saved.")
    st.markdown("</div>", unsafe_allow_html=True)
