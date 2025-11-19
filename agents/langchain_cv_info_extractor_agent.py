import os
import json
import re
from agents.base_agent import BaseAgent
from utils.file_utils import download_pdf_from_url
from utils.pdf_utils import extract_text_from_pdf
from config.langchain_config import LangChainConfig

class LangChainCVInfoExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__("cv_info_extractor_agent")
        self.llm = LangChainConfig.get_llm()

    def can_handle(self, task_type: str) -> bool:
        return task_type in ["extract_profile_info", "extract_cv_info"]

    def perform_task(self, data: dict, context: dict = None):
        cv_url = data.get("cv_url")
        if not cv_url:
            return {"error": "'cv_url' is required for extracting CV info"}
        return self.extract_profile_info(cv_url)

    def clean_llm_json(self, text: str) -> str:
        """
        Remove triple backticks and trim whitespace to extract valid JSON.
        """
        cleaned = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE)
        return cleaned.strip()

    def extract_profile_info(self, cv_url: str):
        try:
            # Prepare file path
            # Extract filename from URL and remove query parameters
            filename = cv_url.split("/")[-1].split("?")[0]
            save_dir = "data/cv_pdfs"
            os.makedirs(save_dir, exist_ok=True)
            file_path = os.path.join(save_dir, filename)

            # Download if not already downloaded
            if not os.path.exists(file_path):
                print(f"Downloading CV: {cv_url}")
                file_path = download_pdf_from_url(cv_url, save_dir, filename)
                if not file_path:
                    return {"error": "Failed to download CV"}

            # Extract text from PDF
            cv_text = extract_text_from_pdf(file_path)
            if not cv_text:
                return {"error": "Failed to extract text from CV"}

            # Prepare prompt for LLM
            prompt = f"""
Extract the following fields from the CV content and return a valid JSON object:

- full_name
- email
- linkedin_url
- github_url

CV CONTENT:
{cv_text[:3000]}

Respond in raw JSON format only. Do NOT include markdown or triple backticks. Use null if any field is missing.
"""

            # Use LangChain-style LLM client if available
            if hasattr(self.llm, 'invoke'):
                from langchain_core.messages import HumanMessage
                result = self.llm.invoke([HumanMessage(content=prompt)])
                try:
                    cleaned = self.clean_llm_json(result.content)
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    return {
                        "error": "LLM returned invalid JSON",
                        "raw_response": result.content
                    }

            # Use OpenAI/Groq-style client
            elif hasattr(self.llm, 'chat'):
                result = self.llm.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.2,
                    max_tokens=512
                )
                try:
                    cleaned = self.clean_llm_json(result.choices[0].message.content)
                    return json.loads(cleaned)
                except json.JSONDecodeError:
                    return {
                        "error": "LLM returned invalid JSON",
                        "raw_response": result.choices[0].message.content
                    }

            else:
                return {"error": "Unsupported LLM client in LangChainConfig"}

        except Exception as e:
            return {"error": str(e)}
