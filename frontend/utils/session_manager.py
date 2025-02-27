import streamlit as st


def initialize_session_state():
    """Initialize session state variables."""
    if "extraction_done" not in st.session_state:
        st.session_state.extraction_done = False
    if "extracted_text" not in st.session_state:
        st.session_state.extracted_text = ""
    if "embedding_done" not in st.session_state:
        st.session_state.embedding_done = False
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "summary" not in st.session_state:
        st.session_state.summary = ""


def reset_extraction_state():
    """Reset extraction state for a new URL."""
    st.session_state.extraction_done = False
    st.session_state.summary = ""


def reset_chat_state():
    """Reset chat state for new embeddings."""
    st.session_state.embedding_done = False
    st.session_state.chat_history = []


def reset_all_state():
    """Reset all session state."""
    st.session_state.extraction_done = False
    st.session_state.extracted_text = ""
    st.session_state.embedding_done = False
    st.session_state.chat_history = []
    st.session_state.summary = ""