# File paths
FAISS_INDEX_PATH = "faiss_index"
TEMP_MARKDOWN_PATH = "output.md"
CHAT_HISTORY_PATH = "chat_history.txt"

# Model types
MODEL_TYPE_CLOSED = "Closed Source"
MODEL_TYPE_OPEN = "Open Source"

# Prompt templates
SUMMARY_PROMPT_TEMPLATE = """
You are an AI assistant that is tasked with summarizing a web page.
Your summary should be detailed and cover all key points mentioned in the web page.
Below is the extracted content of the web page:
{content}

Please provide a comprehensive and detailed summary in Markdown format.
"""

QA_PROMPT_TEMPLATE = """
You are an AI assistant tasked with answering questions based solely
on the provided context. Your goal is to generate a comprehensive answer
for the given question using only the information available in the context.

context: {context}

question: {question}

<response> Your answer in Markdown format. </response>
"""