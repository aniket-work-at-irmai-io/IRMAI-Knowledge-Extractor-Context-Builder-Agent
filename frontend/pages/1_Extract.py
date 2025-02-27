import streamlit as st
import os  # Add this import here
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
        url_input = st.text_input("Enter comma-separated URLs to crawl:")
        submit_url = st.form_submit_button("Submit URLs")
        if submit_url and url_input:
            # Reset any previous extraction state
            reset_extraction_state()
            # Split the input by comma and strip whitespace
            urls = [url.strip() for url in url_input.split(',') if url.strip()]
            return urls
    return None


def render_extraction_section(urls):
    """Render the website extraction section."""
    st.header(EXTRACTION_TITLE)

    if not st.session_state.extraction_done:
        with st.spinner("Extracting websites..."):
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

            if selected_file:
                # Add a button to summarize just this file
                if st.button("Summarize Selected File Only"):
                    with st.spinner("Summarizing selected file..."):
                        try:
                            with open(selected_file, "r", encoding="utf-8") as f:
                                file_content = f.read()

                            # Call the API to summarize the selected file
                            response = post_request(
                                API_SUMMARIZE_URL,
                                {
                                    "request": {
                                        "text": file_content
                                    },
                                    "model_type": {
                                        "model_type": MODEL_TYPE_CLOSED
                                    }
                                }
                            )

                            if response.get("status") == "success":
                                st.session_state.summary = response.get("summary", "")
                                st.success(f"Summarization of {os.path.basename(selected_file)} complete!")
                            else:
                                st.error(f"Error: {response.get('message', 'Unknown error')}")
                        except Exception as e:
                            st.error(f"Error during file summarization: {str(e)}")

        st.markdown("---")


        st.subheader("Summarize Web Pages")
        if st.button("Summarize Web Pages", key="summarize_button"):
            with st.spinner("Summarizing..."):
                all_extracted_text = ""

                # Debug information
                st.session_state.debug_info = {
                    "files_processed": [],
                    "content_lengths": []
                }

                # Process each file separately with error handling
                for file in st.session_state.extracted_files:
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            file_content = f.read()
                            all_extracted_text += file_content + "\n\n"

                        # Store debug info
                        st.session_state.debug_info["files_processed"].append(file)
                        st.session_state.debug_info["content_lengths"].append(len(file_content))

                    except Exception as e:
                        st.error(f"Error reading file {file}: {str(e)}")

                # Log the total combined text length
                total_length = len(all_extracted_text)
                st.info(
                    f"Combined text from {len(st.session_state.extracted_files)} files. Total length: {total_length} characters.")

                # Check if we have text to summarize
                if not all_extracted_text.strip():
                    st.error("No content to summarize. Please make sure extracted files contain text.")
                    return

                try:
                    # Call the API to summarize the text with more detailed debugging
                    request_data = {
                        "request": {
                            "text": all_extracted_text
                        },
                        "model_type": {
                            "model_type": MODEL_TYPE_CLOSED
                        }
                    }

                    # Log request info
                    st.info(f"Sending summarization request with {len(request_data['request']['text'])} characters")

                    response = post_request(API_SUMMARIZE_URL, request_data)

                    if response.get("status") == "success":
                        st.session_state.summary = response.get("summary", "")
                        st.success("Summarization complete!")
                    else:
                        st.error(f"Error: {response.get('message', 'Unknown error')}")
                        st.info("Response details: " + str(response))
                except Exception as e:
                    st.error(f"Error during summarization API request: {str(e)}")

        if st.session_state.summary:
            st.subheader("Summarized Output")
            st.markdown(st.session_state.summary, unsafe_allow_html=False)

        st.info("Next, go to the 'Embed and Chat' page to create embeddings and chat with the content.")

# URL Input Form
# URL Input Form
urls = render_url_form()

# If URLs have been submitted, show extraction section
if urls:
    render_extraction_section(urls)
elif st.session_state.extraction_done:
    # If extraction was done previously, still show the results
    render_extraction_section(None)
