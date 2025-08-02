from flask import Flask, request, jsonify ,render_template
import requests
import os
from utils.file_utils import download_pdf_from_url
from utils.hash_utils import get_file_hash
from agents.langchain_job_matcher_agent import LangChainJobMatcherAgent, extract_match_score
from database.langchain_vector_db import LangChainVectorDB
from agents.central_managing_ai import run_task
from agents.langchain_cv_info_extractor_agent import LangChainCVInfoExtractorAgent
from agents.langchain_email_generation_agent import LangChainEmailGenerationAgent
from datetime import datetime, timedelta
from agents.langchain_interview_agent import LangChainInterviewAgent


app = Flask(__name__)

def process_application_data(data):
    job_post = data.get("jobPost", {})
    candidates = data.get("candidateList", [])

    job_description = job_post.get("jobDescription", "")
    job_title = job_post.get("jobTitle", "Unknown Job")

    vector_db = LangChainVectorDB()
    matcher = LangChainJobMatcherAgent()

    results = []

    # Load cached CV summaries by file hash
    existing_cv_summaries = vector_db.get_all_cv_summaries()
    hash_to_summary = {
        cv.get("metadata", {}).get("file_hash"): cv["text"]
        for cv in existing_cv_summaries
        if cv.get("metadata", {}).get("file_hash")
    }

    for candidate in candidates:
        full_name = f"{candidate.get('firstName','')} {candidate.get('lastName','')}"
        cv_url = candidate.get("cvURL")
        email = candidate.get("email", "unknown@example.com")
        if not cv_url:
            print(f"Skipping {full_name} - no CV URL")
            continue

        print(f"Processing CV for {full_name} from {cv_url}")

        # Prepare local path for downloaded CV
        cv_filename = cv_url.split("/")[-1]
        local_cv_dir = "data/cv_pdfs"
        os.makedirs(local_cv_dir, exist_ok=True)
        local_cv_path = os.path.join(local_cv_dir, cv_filename)

        # Download if not exists
        if not os.path.exists(local_cv_path):
            downloaded_path = download_pdf_from_url(cv_url, save_dir=local_cv_dir, filename=cv_filename)
            if not downloaded_path:
                print(f"Failed to download CV for {full_name}")
                continue
            local_cv_path = downloaded_path

        # Compute hash
        file_hash = get_file_hash(local_cv_path)

        # Check cached summary
        if file_hash in hash_to_summary:
            cv_summary = hash_to_summary[file_hash]
            print(f"Using cached summary for {full_name}")
        else:
            print(f"Summarizing CV for {full_name}")
            cv_summary = run_task("summarize_cv", cv_path=local_cv_path)
            if "Error" in cv_summary:
                print(f"Error summarizing CV for {full_name}: {cv_summary}")
                continue

            added = vector_db.add_text_document(
                text=cv_summary,
                doc_id=email,
                doc_type="cv_summary",
                file_hash=file_hash,
                email=email  
            )
            if not added:
                print(f"Duplicate detected when adding summary for {full_name}")

            hash_to_summary[file_hash] = cv_summary

        print(f"Matching CV to job '{job_title}' for {full_name}")
        analysis = matcher.match_cv_to_job(cv_summary, job_description)
        score = extract_match_score(analysis)

        results.append({
            "candidate_name": full_name,
            "email": email,
            "score": score,
            "analysis": analysis
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results


@app.route('/trigger_pipeline', methods=['POST'])
def trigger_pipeline():
    content = request.json

    # Expecting full application data under "data"
    if not content or not content.get("data"):
        return jsonify({"success": False, "message": "Missing application data"}), 400

    data = content["data"]  # this contains jobPost, candidateList, etc.
    results = process_application_data(data)

    return jsonify({"success": True, "results": results})


@app.route('/extract_profile', methods=['POST'])
def extract_profile():
    content = request.json
    cv_url = content.get("cvURL")
    if not cv_url:
        return jsonify({"success": False, "message": "Missing cvURL"}), 400

    extractor = LangChainCVInfoExtractorAgent()
    result = extractor.extract_profile_info(cv_url)

    if result.get("error"):
        return jsonify({"success": False, "message": result["error"], "raw": result.get("raw_response", "")}), 500

    return jsonify({"success": True, "profile": result})


@app.route('/generate_emails', methods=['POST'])
def generate_emails():
    data = request.json

    required_fields = ["jobId", "jobTitle", "jobDescription", "closingDate", "candidates"]
    for field in required_fields:
        if field not in data:
            return jsonify({"success": False, "message": f"Missing field: {field}"}), 400

    job_id = data["jobId"]
    job_title = data["jobTitle"]
    job_description = data["jobDescription"]
    closing_date_raw = data["closingDate"]
    candidates = data["candidates"]

    try:
        closing_date = datetime.fromisoformat(closing_date_raw.replace("Z", ""))
    except ValueError:
        return jsonify({"success": False, "message": "Invalid closingDate format"}), 400

    interview_date = (closing_date + timedelta(days=7)).strftime('%Y-%m-%d')
    closing_date_str = closing_date.strftime('%Y-%m-%d')

    email_agent = LangChainEmailGenerationAgent()
    generated_emails = []

    for candidate in candidates:
        try:
            candidate_name = candidate.get("name", "Candidate")
            candidate_email = candidate.get("email", "unknown@example.com")

            email_text = email_agent.generate_email(
                job_description=job_description,
                interview_date=interview_date,
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_title=job_title,
                closing_date=closing_date_str
            )

            generated_emails.append({
                "candidate_name": candidate_name,
                "email": candidate_email,
                "generated_email": email_text
            })

        except Exception as e:
            generated_emails.append({
                "candidate_name": candidate.get("name", "Unknown"),
                "email": candidate.get("email", "unknown@example.com"),
                "error": f"Failed to generate email: {str(e)}"
            })

    return jsonify({
        "success": True,
        "job_id": job_id,
        "job_title": job_title,
        "interview_date": interview_date,
        "closing_date": closing_date_str,
        "emails": generated_emails
    })

@app.route('/generate_interview_questions', methods=['POST'])
def generate_interview_questions():
    content = request.json
    email = content.get("email")
    
    if not email:
        return jsonify({"success": False, "message": "Missing email"}), 400

    agent = LangChainInterviewAgent()
    questions = agent.generate_questions_from_summary(email)

    return jsonify({
        "success": True,
        "email": email,
        "interview_questions": questions
    })

@app.route('/start_interview', methods=['POST'])
def start_interview():
    content = request.json
    email = content.get("email")
    if not email:
        return jsonify({"success": False, "message": "Missing email"}), 400

    agent = LangChainInterviewAgent()
    question = agent.start_interview(email)

    return jsonify({"success": True, "question": question})


@app.route('/next_question', methods=['POST'])
def next_question():
    content = request.json
    email = content.get("email")
    qa_history = content.get("qa_history", [])

    if not email or not qa_history:
        return jsonify({"success": False, "message": "Missing email or qa_history"}), 400

    agent = LangChainInterviewAgent()
    next_q = agent.continue_interview(email, qa_history)

    return jsonify({"success": True, "next_question": next_q})
@app.route('/')
def home():
    # Render the interview bot HTML page
    return render_template('index.html')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
