import streamlit as st
import os
from streamlit_chat import message as st_message
from utils.api_client import post_request
from utils.session_manager import initialize_session_state
from frontend_constants import (
    API_CREATE_EMBEDDINGS_URL,
    API_ASK_QUESTION_URL,
    MODEL_TYPE_CLOSED,
    MODEL_TYPE_OPEN,
    EMBEDDINGS_TITLE,
    CHAT_TITLE,
)

FAISS_INDEX_PATH = "faiss_index"

# Initialize session state
initialize_session_state()

# Set page title
st.title("Create Embeddings & Chat")


def check_embeddings_exist():
    """Check if FAISS index files exist."""
    index_file = os.path.join(FAISS_INDEX_PATH, "index.faiss")
    return os.path.exists(index_file)


def render_embeddings_section():
    """Render the embeddings creation section."""
    st.header(EMBEDDINGS_TITLE)

    embeddings_exist = check_embeddings_exist()

    if not embeddings_exist:
        if st.button("Create Embeddings"):
            create_embeddings()
    else:
        st.success("Embeddings have been created. You can now chat with the content.")

        # Add the "Refresh Embeddings" button
        if st.button("Refresh Embeddings"):
            with st.spinner("Refreshing embeddings..."):

                # Call the API to delete embeddings
                response = post_request(
                    "/api/embeddings/delete",
                    {}
                )

                # Regardless of delete result, we can now create new embeddings
                st.success("Ready to create new embeddings.")
                create_embeddings()
                # Force a rerun to update the UI
                st.rerun()


def create_embeddings():
    with st.spinner("Creating embeddings..."):
        # Use the direct file path method instead of combining texts
        response = post_request(
            "/api/embeddings/create_from_files",
            {"file_paths": st.session_state.extracted_files}
        )

        if response.get("status") == "success":
            st.success("Vectors are created!")
            # Force a rerun to update the UI
            st.rerun()
        else:
            st.error(f"Error: {response.get('message', 'Unknown error')}")


def render_chat_section():
    """Render the chat section."""
    st.header(CHAT_TITLE)

    embeddings_exist = check_embeddings_exist()

    if not embeddings_exist:
        st.info("Please create embeddings first to activate the chat.")
        return

    # Chat interface
    user_input = st.text_input("Your Message:", key="chat_input")
    if st.button("Send", key="send_button") and user_input:
        # Call the API to ask a question
        response = post_request(
            API_ASK_QUESTION_URL,
            {
                "request": {
                    "question": user_input,
                    "model_type": MODEL_TYPE_CLOSED
                },
                "chat_history": {
                    "history": st.session_state.chat_history
                }
            }
        )

        if "answer" in response:
            bot_answer = response["answer"]
            st.session_state.chat_history.append({"user": user_input, "bot": bot_answer})
        else:
            st.error(f"Error: {response.get('message', 'Unknown error')}")

    # Display the conversation using streamlit_chat component with unique keys
    if st.session_state.chat_history:
        for i, chat in enumerate(st.session_state.chat_history):
            # Add unique key for each message based on its index
            st_message(chat["user"], is_user=True, key=f"user_msg_{i}")
            st_message(chat["bot"], is_user=False, key=f"bot_msg_{i}")

# Render both sections
render_embeddings_section()
st.markdown("---")
render_chat_section()