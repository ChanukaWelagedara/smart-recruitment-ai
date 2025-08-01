import requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from collections import defaultdict
from utils.file_utils import download_pdf_from_url
from agents.langchain_job_matcher_agent import LangChainJobMatcherAgent, extract_match_score
from database.langchain_vector_db import LangChainVectorDB
from agents.central_managing_ai import run_task
from utils.hash_utils import get_file_hash

API_URL = "http://localhost:3001/api/applications/688940754e7784a41a38a2b6"


def process_api_job_cvs(api_url):
    # Fetch API response
    response = requests.get(api_url)
    if response.status_code != 200:
        print(f"Failed to fetch API data: {response.status_code}")
        return []
    data = response.json()
    if not data.get("success"):
        print("API response indicates failure")
        return []

    job_post = data["data"]["jobPost"]
    candidates = data["data"]["candidateList"]

    job_description = job_post.get("jobDescription", "")
    print(f"Processing job: {job_post.get('jobTitle')}")

    vector_db = LangChainVectorDB()
    matcher = LangChainJobMatcherAgent()

    results = []

    # Load all CV summaries from vector DB once
    existing_cv_summaries = vector_db.get_all_cv_summaries()

    # Create a map: file_hash -> summary text
    hash_to_summary = {}
    for cv in existing_cv_summaries:
        meta = cv.get("metadata", {})
        fh = meta.get("file_hash")
        if fh:
            hash_to_summary[fh] = cv["text"]

    for candidate in candidates:
        full_name = f"{candidate['firstName']} {candidate['lastName']}"
        cv_url = candidate.get("cvURL")
        if not cv_url:
            print(f"Candidate {full_name} has no CV URL, skipping.")
            continue

        print(f"Checking CV for {full_name} from URL: {cv_url}")

        # Define local file path based on CV file name from URL
        cv_filename = cv_url.split("/")[-1]
        local_cv_dir = "data/cv_pdfs"
        os.makedirs(local_cv_dir, exist_ok=True)
        local_cv_path = os.path.join(local_cv_dir, cv_filename)

        # If file exists locally, compute hash from it
        if os.path.exists(local_cv_path):
            file_hash = get_file_hash(local_cv_path)
            print(f"Found local CV file for {full_name}, hash: {file_hash}")
        else:
            # File doesn't exist locally, download now
            print(f"Downloading CV for {full_name} ...")
            downloaded_path = download_pdf_from_url(cv_url, save_dir=local_cv_dir, filename=cv_filename)
            if not downloaded_path:
                print(f"Failed to download CV for {full_name}, skipping.")
                continue
            file_hash = get_file_hash(downloaded_path)
            local_cv_path = downloaded_path
            print(f"Downloaded CV for {full_name}, hash: {file_hash}")

        # Check if this CV hash already exists in vector DB summaries
        if file_hash in hash_to_summary:
            print(f"Using cached CV summary for {full_name}.")
            cv_summary = hash_to_summary[file_hash]
        else:
            # No cached summary found, summarize and add to DB
            print(f"Summarizing CV for {full_name} ...")
            cv_summary = run_task("summarize_cv", cv_path=local_cv_path)
            if "Error" in cv_summary:
                print(f"Error summarizing CV for {full_name}: {cv_summary}")
                continue

            added = vector_db.add_text_document(
                text=cv_summary,
                doc_id=local_cv_path,
                doc_type="cv_summary",
                file_hash=file_hash
            )
            if not added:
                print(f"Duplicate CV summary detected for {full_name} on adding, skipping.")

            # Update cache map for future candidates if any
            hash_to_summary[file_hash] = cv_summary

        # Match CV summary to job description text from API
        print(f"Matching CV for {full_name} to job '{job_post.get('jobTitle')}' ...")
        analysis = matcher.match_cv_to_job(cv_summary, job_description)
        score = extract_match_score(analysis)

        results.append({
            "candidate_name": full_name,
            "email": candidate.get("email"),
            "score": score,
            "analysis": analysis
        })

    # Sort candidates by match score descending
    results.sort(key=lambda x: x["score"], reverse=True)

    # Output the sorted results
    print("\n=== Sorted Candidates by Match Score ===")
    for r in results:
        print(f"{r['candidate_name']} ({r['email']}): Score {r['score']}%")

    return results


if __name__ == "__main__":
    sorted_candidates = process_api_job_cvs(API_URL)

    import json
    os.makedirs("results", exist_ok=True)
    json_path = "results/sorted_candidates.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(sorted_candidates, f, ensure_ascii=False, indent=2)
    print(f"Saved sorted candidates to {json_path}")
