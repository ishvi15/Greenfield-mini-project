import streamlit as st


def render_project_assignment():
    st.markdown("<div class='section-title'>Project Assignment</div>", unsafe_allow_html=True)
    st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
    project_form = st.form("project_assignment_only")
    with project_form:
        st.write("Project assignment")
        project_name = st.text_input("Project name")
        project_department = st.selectbox("Owner department", ["Engineering", "People", "Finance", "Sales", "Operations", "Marketing"])
        priority = st.selectbox("Priority", ["Low", "Medium", "High", "Critical"])
        allocated_hours = st.number_input("Allocated hours", min_value=10, step=10)
        project_submitted = st.form_submit_button("Create project")
        if project_submitted:
            st.success(f"Project '{project_name}' created and assigned to {project_department}.")
    st.markdown("</div>", unsafe_allow_html=True)
