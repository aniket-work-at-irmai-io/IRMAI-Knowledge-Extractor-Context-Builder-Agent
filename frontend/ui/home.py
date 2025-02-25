import streamlit as st
from frontend_constants import HOME_TITLE, HOME_DESCRIPTION

def render_home_page():
    """Render the home page."""
    st.markdown(f"## {HOME_TITLE}")
    st.markdown(HOME_DESCRIPTION)