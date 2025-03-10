from langchain import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from utils.config_utils import CONFIG
from utils.file_utils import save_chat_history
from services.embeddings_service import EmbeddingsService
from constants import QA_PROMPT_TEMPLATE, MODEL_TYPE_CLOSED, MODEL_TYPE_OPEN, CHAT_HISTORY_PATH
from utils.irmai_utils import get_azure_openai_client


class ChatService:
    @staticmethod
    def get_qa_chain(model_type=MODEL_TYPE_CLOSED):
        """Get a retrieval-based QA chain using the vectorstore."""
        vectorstore = EmbeddingsService.load_embeddings()
        if not vectorstore:
            return None

        # Pass the flag only to the retriever
        retriever = vectorstore.as_retriever(
            search_kwargs={"k": CONFIG["retrieval"]["k"]}
        )

        prompt = PromptTemplate(template=QA_PROMPT_TEMPLATE, input_variables=["context", "question"])
        chain_type_kwargs = {"prompt": prompt}

        # Initialize the appropriate LLM based on selection
        if model_type == MODEL_TYPE_CLOSED:
            # Get Azure OpenAI client (just to ensure it's initialized)
            get_azure_openai_client()

            # Azure OpenAI credentials
            azure_endpoint = "https://smartcall.openai.azure.com/"
            api_key = "abfThcHeAaGdPRna0tPFYEI4yXaz6wLU0uKlDrnPA7llpeyirOJMJQQJ99ALACYeBjFXJ3w3AAABACOGvWJz"
            api_version = "2024-02-01"

            model_name = CONFIG["models"]["openai"]["chat"]
            llm = AzureChatOpenAI(
                deployment_name=model_name,
                azure_endpoint=azure_endpoint,  # Using azure_endpoint instead of openai_api_base
                api_key=api_key,  # Using api_key instead of openai_api_key
                api_version=api_version,  # Using api_version instead of openai_api_version
                temperature=0.3,
                max_tokens=1000
            )
        else:
            model_name = CONFIG["models"]["ollama"]["default"]
            base_url = CONFIG["models"]["ollama"]["base_url"]
            llm = ChatOllama(model=model_name, base_url=base_url, temperature=0.3)

        # Safe parameters that exclude the problematic flag
        params = {
            "llm": llm,
            "chain_type": "stuff",
            "retriever": retriever,
            "return_source_documents": True,
            "chain_type_kwargs": chain_type_kwargs,
            "verbose": True
        }

        # Create QA chain with only the safe parameters
        qa = RetrievalQA.from_chain_type(**params)

        return qa

    @staticmethod
    def ask_question(question, model_type=MODEL_TYPE_CLOSED, chat_history=None):
        """Ask a question to the QA chain and update chat history."""
        qa = ChatService.get_qa_chain(model_type)
        if not qa:
            return {"error": "No embeddings found. Please create embeddings first."}

        response = qa(question)
        bot_answer = response["result"]

        # Update chat history
        if chat_history is None:
            chat_history = []
        else:
            # Convert the dict items back to the proper format if they came from JSON
            chat_history = [
                {"user": item["user"], "bot": item["bot"]}
                for item in chat_history
            ]

        chat_history.append({"user": question, "bot": bot_answer})
        save_chat_history(chat_history, CHAT_HISTORY_PATH)

        return {"answer": bot_answer, "chat_history": chat_history}