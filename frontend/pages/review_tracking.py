import streamlit as st


def render_review_tracking():
    st.markdown("<div class='section-title'>Review Tracking</div>", unsafe_allow_html=True)
    st.markdown("<div class='form-shell'>", unsafe_allow_html=True)
    review_form = st.form("review_entry_only")
    with review_form:
        st.write("Performance review")
        employee_id = st.number_input("Employee ID", min_value=1, step=1)
        score = st.slider("Performance score", 1, 10, 7)
        review_submitted = st.form_submit_button("Submit review")
        if review_submitted:
            st.success(f"Review captured for employee {employee_id} with score {score}.")
    st.markdown("</div>", unsafe_allow_html=True)
