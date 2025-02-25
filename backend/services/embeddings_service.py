import os
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from utils.config_utils import CONFIG, get_api_key
from utils.file_utils import save_text_to_file
from constants import FAISS_INDEX_PATH, TEMP_MARKDOWN_PATH


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

        # Set OpenAI API key
        os.environ["OPENAI_API_KEY"] = get_api_key("OPENAI_API_KEY")

        # Create embeddings using OpenAIEmbeddings
        model = CONFIG["models"]["embedding"]["default"]
        embeddings = OpenAIEmbeddings(model=model)

        # Build a FAISS vectorstore from the documents
        vectorstore = FAISS.from_documents(texts, embeddings)

        # Persist the vectorstore locally
        vectorstore.save_local(FAISS_INDEX_PATH)

        return {"status": "success", "message": "Embeddings created successfully"}

    @staticmethod
    def load_embeddings():
        """Load the embeddings from the local FAISS index."""
        # Set OpenAI API key
        os.environ["OPENAI_API_KEY"] = get_api_key("OPENAI_API_KEY")

        # Create embeddings using OpenAIEmbeddings
        model = CONFIG["models"]["embedding"]["default"]
        embeddings = OpenAIEmbeddings(model=model)

        # Load the FAISS vectorstore
        if os.path.exists(FAISS_INDEX_PATH):
            return FAISS.load_local(FAISS_INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
        else:
            return None
