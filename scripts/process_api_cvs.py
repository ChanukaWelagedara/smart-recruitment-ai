import sys
import os
import requests

# Add the project root directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.langchain_vector_db import LangChainVectorDB
from agents.central_managing_ai import run_task
from utils.file_utils import download_pdf_from_url
from utils.hash_utils import get_file_hash

API_URL = "http://localhost:3001/api/applications/688940754e7784a41a38a2b6"

def summarize_and_store_from_api():
    vector_db = LangChainVectorDB()

    try:
        response = requests.get(API_URL)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch data from API: {e}")
        return

    data = response.json().get("data", {})
    candidates = data.get("candidateList", [])

    for candidate in candidates:
        name = f"{candidate['firstName']} {candidate['lastName']}"
        email = candidate["email"]
        cv_url = candidate["cvURL"]

        print(f"\nProcessing CV for: {name} ({email})")

        # Download CV PDF
        pdf_path = download_pdf_from_url(cv_url)
        if not pdf_path:
            print("Skipping due to download error.")
            continue

        # Summarize the CV using existing summarization agent
        cv_summary = run_task("summarize_cv", cv_path=pdf_path)
        if "Error" in cv_summary:
            print(f"Summary error: {cv_summary}")
            continue

        # Get hash for deduplication
        file_hash = get_file_hash(pdf_path)

        # Use email as unique doc_id in vector DB
        success = vector_db.add_text_document(
            text=cv_summary,
            doc_id=email,
            doc_type="cv_summary",
            file_hash=file_hash
        )

        if success:
            print("Summary stored in vector DB")
        else:
            print("Duplicate CV detected. Skipped.")

if __name__ == "__main__":
    summarize_and_store_from_api()
