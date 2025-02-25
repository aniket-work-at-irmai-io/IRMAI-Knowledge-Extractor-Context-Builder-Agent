import streamlit as st
from frontend_constants import CONTACT_TITLE, CONTACT_INFO

def render_contact_page():
    """Render the contact page."""
    st.markdown(f"## {CONTACT_TITLE}")
    st.markdown(CONTACT_INFO)