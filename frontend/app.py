import streamlit as st
from utils.session_manager import initialize_session_state
from ui.home import render_home_page
from ui.ai_engine import render_ai_engine_page
from ui.contact import render_contact_page
import yaml

# Load configuration
with open("frontend/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Initialize session state
initialize_session_state()

# Set page config
st.set_page_config(
    layout=config["ui"]["layout"],
    page_title=config["ui"]["page_title"]
)

# Set title
st.title(config["ui"]["page_title"])

# Navigation sidebar
pages = config["pages"]
page_names = [p["display_name"] for p in pages]
page = st.sidebar.selectbox("Navigation", page_names)

# Render selected page
if page == "Home":
    render_home_page()
elif page == "AI Engine":
    render_ai_engine_page()
elif page == "Contact":
    render_contact_page()