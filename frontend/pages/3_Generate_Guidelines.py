# 3_Generate_Guidelines.py
import streamlit as st
import os
import glob
from datetime import datetime
from utils.api_client import post_request
from utils.session_manager import initialize_session_state
from frontend_constants import (
    API_GENERATE_GUIDELINES_URL,
    GUIDELINES_TITLE,
)

# Initialize session state
initialize_session_state()

# Set page title
st.title(GUIDELINES_TITLE)

# Check if embeddings exist
embeddings_exist = os.path.exists("faiss_index")

if not embeddings_exist:
    st.warning("Please create embeddings first on the 'Embed and Chat' page.")
else:
    # Check if reference folder exists
    reference_folder = "reference"
    if not os.path.exists(reference_folder):
        os.makedirs(reference_folder, exist_ok=True)
        st.warning(
            f"The '{reference_folder}' folder has been created. Please add reference files before generating guidelines.")

    # Check for reference files
    reference_files = glob.glob(f"{reference_folder}/*.txt")

    # Guidelines section
    st.subheader("Reference Files")

    if reference_files:
        st.write(f"Found {len(reference_files)} reference files:")
        for file in reference_files:
            st.write(f"- {os.path.basename(file)}")
    else:
        st.warning(
            f"No reference files found in '{reference_folder}' folder. Guidelines will be generated based only on embeddings data.")

    # Upload new reference files
    st.subheader("Upload Reference Files")
    uploaded_files = st.file_uploader("Upload reference text files", type=['txt'], accept_multiple_files=True)

    if uploaded_files and st.button("Save Reference Files"):
        for file in uploaded_files:
            file_path = os.path.join(reference_folder, file.name)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(file.getvalue().decode("utf-8"))
        st.success(f"Saved {len(uploaded_files)} reference files.")
        st.rerun()

    # Guidelines generation section
    st.subheader("Generate FX Trade Guidelines")

    if st.button("Generate Guidelines"):
        with st.spinner("Generating guidelines... This may take a while."):
            # Ensure output directory exists
            os.makedirs("guidelines_output", exist_ok=True)

            # Call the API to generate guidelines
            response = post_request(
                API_GENERATE_GUIDELINES_URL,
                {}
            )

            if response.get("status") == "success":
                st.session_state.guidelines = response.get("guidelines", "")
                st.session_state.guidelines_file_path = response.get("file_path", "")
                st.success(
                    f"Guidelines generated successfully and saved to {os.path.basename(st.session_state.guidelines_file_path)}!")
            else:
                st.error(f"Error: {response.get('message', 'Unknown error')}")

    # Display guidelines
    if "guidelines" in st.session_state and st.session_state.guidelines:
        st.subheader("Generated Guidelines")
        st.markdown(st.session_state.guidelines)

        # Provide a download button for the guidelines
        if "guidelines_file_path" in st.session_state and st.session_state.guidelines_file_path:
            try:
                with open(st.session_state.guidelines_file_path, "r", encoding="utf-8") as f:
                    guidelines_content = f.read()
                    st.download_button(
                        label="Download Guidelines",
                        data=guidelines_content,
                        file_name=os.path.basename(st.session_state.guidelines_file_path),
                        mime="text/plain",
                    )
            except Exception as e:
                st.error(f"Error reading guidelines file: {str(e)}")

    # Previous guidelines
    st.subheader("Previous Guidelines")
    if os.path.exists("guidelines_output"):
        previous_files = sorted(glob.glob("guidelines_output/*.txt"), key=os.path.getmtime, reverse=True)
        if previous_files:
            selected_file = st.selectbox(
                "Select a previously generated guideline:",
                options=previous_files,
                format_func=os.path.basename
            )

            if selected_file:
                try:
                    with open(selected_file, "r", encoding="utf-8") as f:
                        previous_content = f.read()
                        st.text_area("Preview", previous_content[:500] + "...", height=150)
                        st.download_button(
                            label="Download Selected Guidelines",
                            data=previous_content,
                            file_name=os.path.basename(selected_file),
                            mime="text/plain",
                        )
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        else:
            st.info("No previously generated guidelines found.")