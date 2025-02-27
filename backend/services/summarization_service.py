from langchain import PromptTemplate
from langchain_openai import AzureChatOpenAI
from langchain_ollama import ChatOllama
from utils.config_utils import CONFIG
from constants import SUMMARY_PROMPT_TEMPLATE, MODEL_TYPE_CLOSED, MODEL_TYPE_OPEN
from utils.irmai_utils import get_azure_openai_client


class SummarizationService:
    # In summarization_service.py, modify the summarize_text method:
    @staticmethod
    def summarize_text(content, model_type=MODEL_TYPE_CLOSED):
        """Summarize the extracted content using a language model."""
        # Check content length
        content_length = len(content)

        # Create a robust summary prompt
        summary_prompt = PromptTemplate(template=SUMMARY_PROMPT_TEMPLATE, input_variables=["content"])
        prompt_text = summary_prompt.format(content=content)

        try:
            if model_type == MODEL_TYPE_CLOSED:
                # Get Azure OpenAI client (just to ensure it's initialized)
                get_azure_openai_client()

                # Azure OpenAI credentials
                azure_endpoint = "https://smartcall.openai.azure.com/"
                api_key = "abfThcHeAaGdPRna0tPFYEI4yXaz6wLU0uKlDrnPA7llpeyirOJMJQQJ99ALACYeBjFXJ3w3AAABACOGvWJz"
                api_version = "2024-02-01"

                model_name = CONFIG["models"]["openai"]["summarization"]
                summarizer = AzureChatOpenAI(
                    deployment_name=model_name,
                    azure_endpoint=azure_endpoint,  # Using azure_endpoint instead of openai_api_base
                    api_key=api_key,  # Using api_key instead of openai_api_key
                    api_version=api_version,  # Using api_version instead of openai_api_version
                    temperature=0.3,
                    max_tokens=1500
                )
            else:
                model_name = CONFIG["models"]["ollama"]["default"]
                base_url = CONFIG["models"]["ollama"]["base_url"]
                summarizer = ChatOllama(model=model_name, base_url=base_url, temperature=0.3)

            # Get the summary
            summary_response = summarizer(prompt_text)
            return summary_response.content
        except Exception as e:
            # Log the error for debugging
            print(f"Error in summarization: {str(e)}")
            raise e