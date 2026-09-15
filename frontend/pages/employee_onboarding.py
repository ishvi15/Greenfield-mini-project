import streamlit as st


def render_employee_onboarding():
    st.markdown("<div class='section-title'>Employee Onboarding</div>", unsafe_allow_html=True)
    st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
    employee_form = st.form("employee_onboarding_only")
    with employee_form:
        st.write("Employee onboarding")
        first_name = st.text_input("First name")
        last_name = st.text_input("Last name")
        department = st.selectbox("Department", ["Engineering", "People", "Finance", "Sales", "Operations", "Marketing"])
        role = st.text_input("Role")
        salary = st.number_input("Salary", min_value=30000, step=1000)
        submitted = st.form_submit_button("Add employee")
        if submitted:
            st.success(f"Employee {first_name} {last_name} ready for onboarding into the OLTP system.")
    st.markdown("</div>", unsafe_allow_html=True)
