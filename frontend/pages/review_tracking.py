import streamlit as st

from backend.db_service import get_last_insert_error, insert_review_record
from backend.data_service import load_live_data


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
            if insert_review_record(employee_id, score, "Engineering"):
                load_live_data.clear()
                st.session_state["flash_message"] = f"Review saved for employee {employee_id}."
                st.rerun()
            else:
                st.error(get_last_insert_error() or "Review could not be saved.")
    st.markdown("</div>", unsafe_allow_html=True)
