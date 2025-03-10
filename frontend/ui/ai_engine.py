import streamlit as st
from streamlit_chat import message as st_message
from utils.api_client import post_request
from frontend_constants import (
    API_EXTRACT_URL,
    API_SUMMARIZE_URL,
    API_CREATE_EMBEDDINGS_URL,
    API_ASK_QUESTION_URL,
    MODEL_TYPE_CLOSED,
    MODEL_TYPE_OPEN,
    EXTRACTION_TITLE,
    EMBEDDINGS_TITLE,
    CHAT_TITLE,
)
from utils.session_manager import reset_session_state


def render_url_form():
    """Render the URL input form."""
    with st.form("url_form"):
        url_input = st.text_input("Enter comma-separated URLs to crawl:")
        submit_url = st.form_submit_button("Submit URLs")
        if submit_url and url_input:
            st.session_state.url_submitted = True
            # Reset any previous state
            reset_session_state()
            # Split the input by comma and strip whitespace
            urls = [url.strip() for url in url_input.split(',') if url.strip()]
            return urls
    return None


def render_extraction_column(urls):
    """Render the website extraction column."""
    st.header(EXTRACTION_TITLE)

    if not st.session_state.extraction_done:
        with st.spinner("Extracting websites..."):
            # Create crawl_data folder if it doesn't exist
            import os
            os.makedirs("crawl_data", exist_ok=True)

            # Keep track of extraction success for each URL
            extraction_success = []

            for i, url in enumerate(urls):
                # Call the API to extract the website
                response = post_request(API_EXTRACT_URL, {"url": url})
                if response.get("status") == "success":
                    # Save the extracted text to a file
                    filename = f"crawl_data/url_{i}_{url.replace('://', '_').replace('/', '_').replace(':', '_')}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(response.get("text", ""))
                    extraction_success.append((url, True, filename))
                else:
                    st.error(f"Error extracting {url}: {response.get('message', 'Unknown error')}")
                    extraction_success.append((url, False, None))

            # Set extraction as done if at least one URL was extracted successfully
            successful_extractions = [item for item in extraction_success if item[1]]
            if successful_extractions:
                st.session_state.extraction_done = True
                st.success(f"Extraction complete for {len(successful_extractions)} out of {len(urls)} URLs!")

                # Store the list of successfully extracted files in the session state
                st.session_state.extracted_files = [item[2] for item in successful_extractions]
            else:
                st.error("Failed to extract any URLs.")

    # Show a preview of the extracted files
    if st.session_state.extraction_done:
        st.info(
            f"Successfully extracted {len(st.session_state.extracted_files)} URLs. The data is stored in the 'crawl_data' folder.")

        # Provide a dropdown to select a file to preview
        if st.session_state.extracted_files:
            selected_file = st.selectbox("Select a file to preview:", st.session_state.extracted_files)
            if selected_file:
                with open(selected_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    preview = "\n".join([line for line in content.splitlines() if line.strip()][:5])
                st.text_area("Extracted Text Preview", preview, height=150)

                # Provide a download button for the selected file
                with open(selected_file, "r", encoding="utf-8") as f:
                    st.download_button(
                        label="Download Selected File",
                        data=f.read(),
                        file_name=os.path.basename(selected_file),
                        mime="text/plain",
                    )

        st.markdown("---")
        st.subheader("Summarize Web Pages")
        if st.button("Summarize Web Page", key="summarize_button"):
            with st.spinner("Summarizing..."):
                all_extracted_text = ""
                for file in st.session_state.extracted_files:
                    with open(file, "r", encoding="utf-8") as f:
                        all_extracted_text += f.read() + "\n\n"

                # Call the API to summarize the text
                response = post_request(
                    API_SUMMARIZE_URL,
                    {
                        "request": {
                            "text": all_extracted_text
                        },
                        "model_type": {
                            "model_type": MODEL_TYPE_CLOSED
                        }
                    }
                )

                if response.get("status") == "success":
                    st.session_state.summary = response.get("summary", "")
                    st.success("Summarization complete!")
                else:
                    st.error(f"Error: {response.get('message', 'Unknown error')}")

        if st.session_state.summary:
            st.subheader("Summarized Output")
            st.markdown(st.session_state.summary, unsafe_allow_html=False)


def render_embeddings_column():
    """Render the embeddings creation column."""
    st.header(EMBEDDINGS_TITLE)

    if st.session_state.extraction_done and not st.session_state.embedding_done:
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
    elif st.session_state.embedding_done:
        st.info("Embeddings have been created.")


def render_chat_column():
    """Render the chat column."""
    st.header(CHAT_TITLE)

    if st.session_state.embedding_done:
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
    else:
        st.info("Please create embeddings to activate the chat.")


def render_ai_engine_page():
    """Render the AI Engine page."""
    # URL Input Form
    urls = render_url_form()

    # If URL has been submitted, divide layout into three columns
    if st.session_state.url_submitted:
        col1, col2, col3 = st.columns(3)

        with col1:
            render_extraction_column(urls)

        with col2:
            render_embeddings_column()

        with col3:
            render_chat_column()