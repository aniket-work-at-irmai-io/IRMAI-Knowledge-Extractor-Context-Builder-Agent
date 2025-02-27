import streamlit as st
from utils.api_client import post_request
from utils.session_manager import initialize_session_state, reset_extraction_state
from frontend_constants import (
    API_EXTRACT_URL,
    API_SUMMARIZE_URL,
    MODEL_TYPE_CLOSED,
    EXTRACTION_TITLE,
)

# Initialize session state
initialize_session_state()

# Set page title
st.title("Website Extraction")

def render_url_form():
    """Render the URL input form."""
    with st.form("url_form"):
        url_input = st.text_input("Enter a URL to crawl:")
        submit_url = st.form_submit_button("Submit URL")
        if submit_url and url_input:
            # Reset any previous extraction state
            reset_extraction_state()
            return url_input
    return None

def render_extraction_section(url):
    """Render the website extraction section."""
    st.header(EXTRACTION_TITLE)

    if not st.session_state.extraction_done:
        with st.spinner("Extracting website..."):
            # Call the API to extract the website
            response = post_request(API_EXTRACT_URL, {"url": url})
            if response.get("status") == "success":
                st.session_state.extracted_text = response.get("text", "")
                st.session_state.extraction_done = True
                st.success("Extraction complete!")
            else:
                st.error(f"Error: {response.get('message', 'Unknown error')}")

    # Show a preview (first few non-empty lines)
    if st.session_state.extraction_done:
        preview = "\n".join(
            [line for line in st.session_state.extracted_text.splitlines() if line.strip()][:5]
        )
        st.text_area("Extracted Text Preview", preview, height=150)

        # Save the full extracted text as a file and provide a download button.
        st.download_button(
            label="Download Extracted Text",
            data=st.session_state.extracted_text,
            file_name="extracted_text.txt",
            mime="text/plain",
        )

        st.markdown("---")
        st.subheader("Summarize Web Page")
        if st.button("Summarize Web Page", key="summarize_button"):
            with st.spinner("Summarizing..."):
                # Call the API to summarize the text
                response = post_request(
                    API_SUMMARIZE_URL,
                    {
                        "request": {
                            "text": st.session_state.extracted_text
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

        st.info("Next, go to the 'Embed and Chat' page to create embeddings and chat with the content.")

# URL Input Form
url = render_url_form()

# If URL has been submitted, show extraction section
if url:
    render_extraction_section(url)
elif st.session_state.extraction_done:
    # If extraction was done previously, still show the results
    render_extraction_section(None)