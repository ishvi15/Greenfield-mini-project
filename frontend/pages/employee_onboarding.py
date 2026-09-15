import streamlit as st

from backend.db_service import get_last_insert_error, insert_employee_record
from backend.data_service import load_live_data
from backend.department_service import DEPARTMENTS


def render_employee_onboarding():
    st.markdown("<div class='section-title'>Employee Onboarding</div>", unsafe_allow_html=True)
    st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
    employee_form = st.form("employee_onboarding_only")
    with employee_form:
        st.write("Employee onboarding")
        first_name = st.text_input("First name")
        last_name = st.text_input("Last name")
        department = st.selectbox("Department", DEPARTMENTS)
        role = st.text_input("Role")
        salary = st.number_input("Salary", min_value=30000, step=1000)
        submitted = st.form_submit_button("Add employee")
        if submitted:
            if insert_employee_record(first_name, last_name, department, role, salary):
                load_live_data.clear()
                st.success(f"Employee {first_name} {last_name} added to the OLTP system.")
            else:
                st.error(get_last_insert_error() or "Employee could not be added to the OLTP system.")
    st.markdown("</div>", unsafe_allow_html=True)
