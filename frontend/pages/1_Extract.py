import streamlit as st
import os
import glob
from datetime import datetime
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
st.title("Website Extraction and File Upload")

# Initialize crawl_data directory if it doesn't exist
os.makedirs("crawl_data", exist_ok=True)


# Load all existing files from crawl_data directory into session state
def load_existing_files():
    if not st.session_state.extracted_files or len(st.session_state.extracted_files) == 0:
        # Get all txt files from the crawl_data directory
        existing_files = glob.glob("crawl_data/*.txt")
        if existing_files:
            st.session_state.extracted_files = existing_files
            st.session_state.extraction_done = True


# Call this function to initialize
load_existing_files()


def render_url_form():
    """Render the URL input form."""
    with st.form("url_form"):
        url_input = st.text_input("Enter comma-separated URLs to crawl:")
        submit_url = st.form_submit_button("Submit URLs")
        if submit_url and url_input:
            # We're not resetting extraction state here anymore
            # Just process the new URLs and add to existing files

            # Split the input by comma and strip whitespace
            urls = [url.strip() for url in url_input.split(',') if url.strip()]
            return urls
    return None


def render_file_upload():
    """Render the file upload section."""
    st.subheader("Or Upload Files")
    uploaded_files = st.file_uploader("Upload PDF, Text, or CSV files", type=['pdf', 'txt', 'csv'],
                                      accept_multiple_files=True)

    if uploaded_files and st.button("Process Uploaded Files"):
        # Process the files without resetting previous ones
        process_uploaded_files(uploaded_files)
        return True
    return False


def process_uploaded_files(uploaded_files):
    """Process uploaded files and save them to crawl_data directory."""
    # Keep track of extraction success for each file
    extraction_success = []

    for i, file in enumerate(uploaded_files):
        try:
            # Generate timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # Clean filename to be filesystem-friendly
            safe_filename = file.name.replace('/', '_').replace(':', '_')

            # Create a standardized filename format
            filename = f"crawl_data/file_{i}_{safe_filename}_{timestamp}.txt"

            # Read file content based on file type
            content = ""
            if file.type == "application/pdf":
                # For PDFs, use PyPDF2 or another PDF processing library
                try:
                    import PyPDF2
                    from io import BytesIO

                    pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
                    content = ""
                    for page_num in range(len(pdf_reader.pages)):
                        content += pdf_reader.pages[page_num].extract_text() + "\n"
                except ImportError:
                    content = f"PDF processing requires PyPDF2 library. Please install it with 'pip install PyPDF2'.\n"
                    st.warning("PDF processing requires PyPDF2 library. Using placeholder text.")
            elif file.type == "text/csv":
                # For CSVs, read as text for now
                content = file.getvalue().decode("utf-8")
            else:
                # For TXT and other files, read directly
                content = file.getvalue().decode("utf-8")

            # Save the content to a file
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            extraction_success.append((file.name, True, filename))

        except Exception as e:
            st.error(f"Error processing {file.name}: {str(e)}")
            extraction_success.append((file.name, False, None))

    # Set extraction as done if at least one file was processed successfully
    successful_extractions = [item for item in extraction_success if item[1]]
    if successful_extractions:
        st.session_state.extraction_done = True
        st.success(f"Processing complete for {len(successful_extractions)} out of {len(uploaded_files)} files!")

        # Store the list of successfully processed files in the session state
        st.session_state.extracted_files.extend([item[2] for item in successful_extractions])
    else:
        st.error("Failed to process any files.")


def render_extraction_section(urls=None):
    """Render the website extraction section."""
    st.header(EXTRACTION_TITLE)

    # Process new URLs if provided
    if urls:
        with st.spinner("Extracting websites..."):
            # Keep track of extraction success for each URL
            extraction_success = []

            for i, url in enumerate(urls):
                # Call the API to extract the website
                response = post_request(API_EXTRACT_URL, {"url": url})
                if response.get("status") == "success":
                    # Generate timestamp for unique filenames
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

                    # Save the extracted text to a file
                    filename = f"crawl_data/url_{i}_{url.replace('://', '_').replace('/', '_').replace(':', '_')}_{timestamp}.txt"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(response.get("text", ""))
                    extraction_success.append((url, True, filename))
                else:
                    st.error(f"Error extracting {url}: {response.get('message', 'Unknown error')}")
                    extraction_success.append((url, False, None))

            # Update extraction state with successful extractions
            successful_extractions = [item for item in extraction_success if item[1]]
            if successful_extractions:
                st.session_state.extraction_done = True
                st.success(f"Extraction complete for {len(successful_extractions)} out of {len(urls)} URLs!")

                # Store the list of successfully extracted files in the session state
                st.session_state.extracted_files.extend([item[2] for item in successful_extractions])
            else:
                st.error("Failed to extract any URLs.")

    # Show a preview of all extracted files (including previously extracted ones)
    if st.session_state.extraction_done:
        st.info(
            f"Successfully extracted {len(st.session_state.extracted_files)} files. The data is stored in the 'crawl_data' folder.")

        # Provide a dropdown to select a file to preview
        if st.session_state.extracted_files:
            selected_file = st.selectbox("Select a file to preview:", st.session_state.extracted_files)
            if selected_file:
                try:
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
                except Exception as e:
                    st.error(f"Error reading file {selected_file}: {str(e)}")

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

        st.subheader("Summarize All Files")
        if st.button("Summarize All Files", key="summarize_button"):
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
urls = render_url_form()

# File Upload Form
files_uploaded = render_file_upload()

# Show extraction section in all cases where there are files
if urls:
    render_extraction_section(urls)
elif files_uploaded or st.session_state.extraction_done:
    # If files were just uploaded or extraction was done previously, show the results
    render_extraction_section()