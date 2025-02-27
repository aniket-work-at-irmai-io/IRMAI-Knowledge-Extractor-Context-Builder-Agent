import streamlit as st
from utils.session_manager import initialize_session_state
from ui.home import render_home_page
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

# Main page content
render_home_page()

# Add a contact section at the bottom of the home page
st.markdown("---")
render_contact_page()