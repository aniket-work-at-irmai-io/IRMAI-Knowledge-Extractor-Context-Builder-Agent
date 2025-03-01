# backend/services/guidelines_service.py
import os
import glob
from datetime import datetime
from langchain import PromptTemplate
from langchain_openai import AzureChatOpenAI
from utils.config_utils import CONFIG
from utils.file_utils import save_text_to_file, ensure_directory_exists
from services.embeddings_service import EmbeddingsService
from utils.irmai_utils import get_azure_openai_client


class GuidelinesService:
    @staticmethod
    def generate_guidelines():
        """Generate FX trade guidelines using context from FAISS index and reference files."""
        # Step 1: Get context from FAISS index
        vectorstore = EmbeddingsService.load_embeddings()
        faiss_context = ""
        if vectorstore:
            try:
                # Retrieve relevant documents from the vectorstore
                docs = vectorstore.similarity_search("FX trade guidelines regulations compliance", k=50)
                faiss_context = "\n\n".join([doc.page_content for doc in docs])
            except Exception as e:
                print(f"Error retrieving documents from FAISS: {str(e)}")

        # Step 2: Read text files from reference folder
        reference_context = ""
        reference_folder = "reference"
        if os.path.exists(reference_folder):
            for file_path in glob.glob(f"{reference_folder}/*.txt"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        reference_context += f.read() + "\n\n"
                except Exception as e:
                    print(f"Error reading reference file {file_path}: {str(e)}")

        # Step 3: Combine contexts
        combined_context = faiss_context + "\n\n" + reference_context

        # If no context is available, use a default message
        if not combined_context.strip():
            combined_context = "No specific context available. Generate comprehensive FX trade guidelines based on industry best practices."

        # Step 4: Generate guidelines using Azure OpenAI
        # Get Azure OpenAI client
        get_azure_openai_client()

        # Azure OpenAI credentials
        azure_endpoint = "https://smartcall.openai.azure.com/"
        api_key = "abfThcHeAaGdPRna0tPFYEI4yXaz6wLU0uKlDrnPA7llpeyirOJMJQQJ99ALACYeBjFXJ3w3AAABACOGvWJz"
        api_version = "2024-02-01"

        model_name = CONFIG["models"]["openai"]["chat"]
        llm = AzureChatOpenAI(
            deployment_name=model_name,
            azure_endpoint=azure_endpoint,
            api_key=api_key,
            api_version=api_version,
            temperature=0.3,
            max_tokens=4000
        )

        # Prepare the prompt
        prompt_template = """
        Generate a comprehensive, structured set of FX trade processing guidelines to serve as a benchmark for evaluating real-world trade execution and post-trade workflows. The guidelines must be specific, actionable, and measurable to enable systematic comparison against actual processes.

        Structure the guidelines under the following core categories:
        1. **Compliance & Regulatory Adherence**
           * Explicit alignment with relevant regulations (e.g., MiFID II, EMIR, Basel III).
           * Mandatory documentation, reporting standards, and audit requirements.
        2. **Pre-Trade Risk Management**
           * Criteria for credit limits, counterparty risk assessments, and exposure thresholds.
           * Validation of trade parameters (e.g., currency pairs, amounts, settlement dates).
        3. **Trade Execution Protocols**
           * Best practices for price verification, liquidity sourcing, and timestamping.
           * Rules for partial fills, slippage thresholds, and market abuse safeguards.
        4. **Post-Trade Processing**
           * Requirements for confirmation matching, settlement instructions, and netting procedures.
           * Timelines for exception handling, dispute resolution, and failover workflows.
        5. **Operational Controls**
           * Reconciliation processes, system redundancy checks, and data integrity standards.
           * Escalation protocols for deviations (e.g., missed settlements, unauthorized trades).
        6. **Documentation & Auditability**
           * Record-keeping standards for trade lifecycle metadata (e.g., chat logs, order history).
           * Retention policies and audit trail accessibility.

        Include examples of both compliant and non-compliant scenarios to clarify expectations. Prioritize conciseness, regulatory rigor, and adaptability to automated system checks. Ensure guidelines are agnostic to institutional size but enforceable via technical or procedural controls.

        Use the following context to inform your guidelines:

        {context}
        """

        prompt = PromptTemplate(template=prompt_template, input_variables=["context"])
        formatted_prompt = prompt.format(context=combined_context)

        # Call Azure OpenAI
        response = llm.invoke(formatted_prompt)
        guidelines = response.content

        # Step 5: Save guidelines to file
        ensure_directory_exists("guidelines_output")
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        file_path = f"guidelines_output/fx_trade_guidelines_{timestamp}.txt"
        save_text_to_file(guidelines, file_path)

        return {"status": "success", "guidelines": guidelines, "file_path": file_path}