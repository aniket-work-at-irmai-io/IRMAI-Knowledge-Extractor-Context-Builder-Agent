import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from utils.config_utils import CONFIG
from utils.file_utils import save_text_to_file
from constants import FAISS_INDEX_PATH, TEMP_MARKDOWN_PATH
from utils.irmai_utils import get_azure_openai_client


class EmbeddingsService:
    @staticmethod
    def create_embeddings(text):
        """Create embeddings from the extracted text."""
        # Save extracted text to a markdown file
        save_text_to_file(text, TEMP_MARKDOWN_PATH)

        # Load the markdown file using UnstructuredMarkdownLoader
        loader = UnstructuredMarkdownLoader(TEMP_MARKDOWN_PATH)
        data = loader.load()

        # Split the text into chunks using RecursiveCharacterTextSplitter
        chunk_size = CONFIG["embeddings"]["chunk_size"]
        chunk_overlap = CONFIG["embeddings"]["chunk_overlap"]
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_documents(data)

        # Get Azure OpenAI client (just to ensure it's initialized)
        get_azure_openai_client()

        # Azure OpenAI credentials
        azure_endpoint = "https://smartcall.openai.azure.com/"
        api_key = "abfThcHeAaGdPRna0tPFYEI4yXaz6wLU0uKlDrnPA7llpeyirOJMJQQJ99ALACYeBjFXJ3w3AAABACOGvWJz"
        api_version = "2024-02-01"

        # Create embeddings using AzureOpenAIEmbeddings
        model = CONFIG["models"]["embedding"]["default"]
        embeddings = AzureOpenAIEmbeddings(
            deployment=model,  # Azure deployment name
            azure_endpoint=azure_endpoint,  # Using azure_endpoint instead of openai_api_base
            api_key=api_key,  # Using api_key instead of openai_api_key
            api_version=api_version  # Using api_version instead of openai_api_version
        )

        # Build a FAISS vectorstore from the documents
        vectorstore = FAISS.from_documents(texts, embeddings)

        # Persist the vectorstore locally
        vectorstore.save_local(FAISS_INDEX_PATH)

        return {"status": "success", "message": "Embeddings created successfully"}

    @staticmethod
    def load_embeddings():
        """Load the embeddings from the local FAISS index."""
        # Get Azure OpenAI client (just to ensure it's initialized)
        get_azure_openai_client()

        # Azure OpenAI credentials
        azure_endpoint = "https://smartcall.openai.azure.com/"
        api_key = "abfThcHeAaGdPRna0tPFYEI4yXaz6wLU0uKlDrnPA7llpeyirOJMJQQJ99ALACYeBjFXJ3w3AAABACOGvWJz"
        api_version = "2024-02-01"

        # Create embeddings using AzureOpenAIEmbeddings
        model = CONFIG["models"]["embedding"]["default"]
        embeddings = AzureOpenAIEmbeddings(
            deployment=model,  # Azure deployment name
            azure_endpoint=azure_endpoint,  # Using azure_endpoint instead of openai_api_base
            api_key=api_key,  # Using api_key instead of openai_api_key
            api_version=api_version  # Using api_version instead of openai_api_version
        )

        # Load the FAISS vectorstore
        if os.path.exists(FAISS_INDEX_PATH):
            return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            return None