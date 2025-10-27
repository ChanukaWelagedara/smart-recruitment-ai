import sys
import glob
from agents.central_managing_ai import run_task
from utils.pdf_utils import extract_text_from_pdf
from database.langchain_vector_db import LangChainVectorDB
from utils.file_utils import get_file_hash


# Import your new function
from agents.match_all_cvs_jobs import match_all_cvs_to_all_jobs
def summarize_cvs(vector_db):
    cv_paths = glob.glob("data/cv_pdfs/*.pdf")
    for cv_path in cv_paths:
        print(f"\nSummarizing CV: {cv_path}")
        cv_summary = run_task("summarize_cv", cv_path=cv_path)

        if "Error" in cv_summary:
            print(f"Failed to summarize CV: {cv_summary}")
            continue

       
        file_hash = get_file_hash(cv_path)

        success = vector_db.add_text_document(
            text=cv_summary,
            doc_id=cv_path,
            doc_type="cv_summary",
            file_hash=file_hash
        )

        if success:
            print("Summary stored in vector DB")
        else:
            print("Duplicate CV detected. Skipped.")

def match_cvs(vector_db):
    job_paths = glob.glob("data/job_ads/*.pdf")
    cv_summaries = vector_db.get_all_cv_summaries()

    if not cv_summaries:
        print("No CV summaries found in vector DB.")
        return

    for cv in cv_summaries:
        summary = cv.get('summary') or cv.get('content')
        if not summary:
            print(f"Skipping CV (missing summary): {cv}")
            continue

        print(f"\nMatching CV: {cv.get('doc_id') or cv.get('source') or '[unknown]'}")
        for job_path in job_paths:
            print(f"   ➜ Against Job: {job_path}")
            job_text = extract_text_from_pdf(job_path)
            result = run_task("match_cv", cv_summary=summary, job_summary=job_text)
            print(result)




def main():
    vector_db = LangChainVectorDB()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py [summarize_cv | match_cv | interview | match_all]")
        return
    
    task = sys.argv[1].lower()

    if task == "summarize_cv":
        summarize_cvs(vector_db)
    elif task == "match_cv":
        match_cvs(vector_db)
    elif task == "match_all":
        match_all_cvs_to_all_jobs()
    else:
        print(f"Unknown task: {task}")

if __name__ == "__main__":
    main()





