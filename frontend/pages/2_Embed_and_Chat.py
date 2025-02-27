import streamlit as st
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

# Initialize session state
initialize_session_state()

# Set page title
st.title("Create Embeddings & Chat")


def render_embeddings_section():
    """Render the embeddings creation section."""
    st.header(EMBEDDINGS_TITLE)

    if not st.session_state.extraction_done:
        st.warning("Please extract website content first on the Extract page.")
        return

    if not st.session_state.embedding_done:
        if st.button("Create Embeddings"):
            with st.spinner("Creating embeddings..."):
                # Combine all extracted texts
                all_extracted_text = ""
                for file in st.session_state.extracted_files:
                    with open(file, "r", encoding="utf-8") as f:
                        all_extracted_text += f.read() + "\n\n"

                # Call the API to create embeddings
                response = post_request(
                    API_CREATE_EMBEDDINGS_URL,
                    {"text": all_extracted_text}
                )

                if response.get("status") == "success":
                    st.session_state.embedding_done = True
                    st.success("Vectors are created!")
                else:
                    st.error(f"Error: {response.get('message', 'Unknown error')}")
    else:
        st.info("Embeddings have been created. You can now chat with the content.")

        # Add the "Refresh Embeddings" button
        if st.button("Refresh Embeddings"):
            with st.spinner("Refreshing embeddings..."):
                # Reset the embedding state first
                st.session_state.embedding_done = False

                # Call the API to delete embeddings (if they exist)
                response = post_request(
                    "/api/embeddings/delete",  # We'll create this endpoint
                    {}
                )

                # Regardless of delete result, we can now create new embeddings
                st.success("Ready to create new embeddings.")
                # Force a rerun to update the UI
                st.rerun()


def render_chat_section():
    """Render the chat section."""
    st.header(CHAT_TITLE)

    if not st.session_state.extraction_done:
        return

    if not st.session_state.embedding_done:
        st.info("Please create embeddings first to activate the chat.")
        return

    # Let the user select the LLM type
    llm_choice = st.radio("Select LLM Type", (MODEL_TYPE_CLOSED, MODEL_TYPE_OPEN), index=0, key="llm_choice")

    # Chat interface
    user_input = st.text_input("Your Message:", key="chat_input")
    if st.button("Send", key="send_button") and user_input:
        # Call the API to ask a question
        response = post_request(
            API_ASK_QUESTION_URL,
            {
                "request": {
                    "question": user_input,
                    "model_type": llm_choice
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

    # Display the conversation using streamlit_chat component
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            st_message(chat["user"], is_user=True)
            st_message(chat["bot"], is_user=False)

# Render both sections
render_embeddings_section()
st.markdown("---")
render_chat_section()