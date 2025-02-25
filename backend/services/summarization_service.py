from langchain import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from utils.config_utils import CONFIG
from constants import SUMMARY_PROMPT_TEMPLATE, MODEL_TYPE_CLOSED, MODEL_TYPE_OPEN


class SummarizationService:
    @staticmethod
    def summarize_text(content, model_type=MODEL_TYPE_CLOSED):
        """Summarize the extracted content using a language model."""
        summary_prompt = PromptTemplate(template=SUMMARY_PROMPT_TEMPLATE, input_variables=["content"])
        prompt_text = summary_prompt.format(content=content)

        if model_type == MODEL_TYPE_CLOSED:
            model_name = CONFIG["models"]["openai"]["summarization"]
            summarizer = ChatOpenAI(model_name=model_name, temperature=0.3, max_tokens=1500)
        else:
            model_name = CONFIG["models"]["ollama"]["default"]
            base_url = CONFIG["models"]["ollama"]["base_url"]
            summarizer = ChatOllama(model=model_name, base_url=base_url, temperature=0.3)

        summary_response = summarizer(prompt_text)
        return summary_response.content