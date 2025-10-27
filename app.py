from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import traceback

from agents.task_manager import TaskManager

from agents.langchain_cv_summary_agent import LangChainCVSummaryAgent
from agents.langchain_job_matcher_agent import LangChainJobMatcherAgent
from agents.langchain_interview_agent import LangChainInterviewAgent
from agents.langchain_email_generation_agent import LangChainEmailGenerationAgent
from agents.langchain_cv_info_extractor_agent import LangChainCVInfoExtractorAgent
from agents.file_download_agent import FileDownloadAgent
from agents.data_privacy_agent import DataPrivacyAgent
from agents.job_post_generation_agent import JobPostGenerationAgent 
from agents.general_interview_agent import GeneralInterviewAgent

# Setup agents
existing_agents = [
    LangChainCVSummaryAgent(),
    LangChainJobMatcherAgent(),
    LangChainInterviewAgent(),
    GeneralInterviewAgent(),
    LangChainEmailGenerationAgent(),
    LangChainCVInfoExtractorAgent(),
    JobPostGenerationAgent()
]
infrastructure_agents = [FileDownloadAgent()]
safeguard_agents = [DataPrivacyAgent()]
all_agents = existing_agents + infrastructure_agents + safeguard_agents

# Create instance
task_manager = TaskManager(all_agents)

app = Flask(__name__)

@app.route('/trigger_pipeline', methods=['POST'])
def trigger_pipeline():
    content = request.json
    if not content or not content.get("data"):
        return jsonify({"success": False, "message": "Missing application data"}), 400

    data = content["data"]
    job_post = data.get("jobPost", {})
    candidates = data.get("candidateList", [])

    results = task_manager.orchestrate_application(job_post, candidates)
    return jsonify({"success": True, "results": results})

@app.route('/extract_profile', methods=['POST'])
def extract_profile():
    content = request.json
    cv_url = content.get("cvURL")
    if not cv_url:
        return jsonify({"success": False, "message": "Missing cvURL"}), 400

    result = task_manager.run_task("extract_profile_info", {"cv_url": cv_url})
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

    generated_emails = []
    for candidate in candidates:
        candidate_name = candidate.get("name", "Candidate")
        candidate_email = candidate.get("email", "unknown@example.com")

        email_text = task_manager.run_task("send_email", {
            "job_description": job_description,
            "interview_date": interview_date,
            "candidate_name": candidate_name,
            "candidate_email": candidate_email,
            "job_title": job_title,
            "closing_date": closing_date_str
        })

        generated_emails.append({
            "candidate_name": candidate_name,
            "email": candidate_email,
            "generated_email": email_text
        })

    return jsonify({
        "success": True,
        "job_id": job_id,
        "job_title": job_title,
        "interview_date": interview_date,
        "closing_date": closing_date_str,
        "emails": generated_emails
    })


@app.route('/api/generate_job_post', methods=['POST'])
def generate_job_post():
    data = request.json or {}

    # Basic validation
    required = ["job_title", "qualifications", "salary", "responsibilities"]
    missing = [r for r in required if r not in data]
    if missing:
        # allow alternative camelCase names too
        alt_missing = []
        for r in missing:
            camel = ''.join([r.split('_')[0]] + [p.capitalize() for p in r.split('_')[1:]])
            if camel in data:
                continue
            alt_missing.append(r)
        if alt_missing:
            return jsonify({"status": "error", "message": f"Missing fields: {', '.join(alt_missing)}"}), 400

    result = task_manager.run_task("generate_job_post", {
        "job_title": data.get("job_title") or data.get("jobTitle"),
        "qualifications": data.get("qualifications") or data.get("qualifications"),
        "salary": data.get("salary"),
        "responsibilities": data.get("responsibilities") or data.get("responsibilities")
    })

    # If the agent returned an error dict, forward it
    if isinstance(result, dict) and result.get("status") == "error":
        return jsonify(result), 500

    # If agent returned structured response
    if isinstance(result, dict) and result.get("status") == "success":
        return jsonify(result)

    # Unexpected return type - try to coerce
    try:
        formatted = str(result)
        return jsonify({"status": "success", "formatted_job_post": formatted})
    except Exception as e:
        return jsonify({"status": "error", "message": "Unable to generate job post", "error": str(e)}), 500

@app.route('/generate_interview_questions', methods=['POST'])
def generate_interview_questions():
    content = request.json
    email = content.get("email")
    if not email:
        return jsonify({"success": False, "message": "Missing email"}), 400

    questions = task_manager.run_task("generate_interview_questions", {"email": email})
    return jsonify({"success": True, "email": email, "interview_questions": questions})

@app.route('/start_interview', methods=['POST'])
def start_interview():
    content = request.json
    email = content.get("email")
    if not email:
        return jsonify({"success": False, "message": "Missing email"}), 400

    # Pass task_type in data dict explicitly
    result = task_manager.run_task("start_interview", {"task_type": "start_interview", "email": email})

    # The result should be a string question; if it's dict with error, handle it
    if isinstance(result, dict) and "error" in result:
        return jsonify({"success": False, "message": result["error"]}), 500

    # Make sure question is a string (if it's an object, try to convert)
    question_text = result if isinstance(result, str) else str(result)

    return jsonify({"success": True, "question": question_text})

@app.route('/start_general_interview', methods=['POST'])
def start_general_interview():
    content = request.json or {}
    email = content.get("email")
    if not email:
        return jsonify({"success": False, "message": "Missing email"}), 400

    result = task_manager.run_task("start_general_interview", {"task_type": "start_general_interview", "email": email})

    # Forward agent response
    if isinstance(result, dict) and result.get("success") is False:
        return jsonify(result), 500

    question = result.get("question") if isinstance(result, dict) else str(result)
    return jsonify({"success": True, "question": question})


@app.route('/answer_general', methods=['POST'])
def answer_general():
    content = request.json or {}
    email = content.get("email")
    answer = content.get("answer")

    if not email or answer is None:
        return jsonify({"success": False, "message": "Missing email or answer"}), 400

    result = task_manager.run_task("answer_general", {"task_type": "answer_general", "email": email, "answer": answer})

    # result expected to be agent dict; forward as-is
    return jsonify(result)

@app.route('/next_question', methods=['POST'])
def next_question():
    content = request.json
    email = content.get("email")
    qa_history = content.get("qa_history", [])

    if not email or not qa_history:
        return jsonify({"success": False, "message": "Missing email or qa_history"}), 400

    # Pass task_type explicitly
    next_q = task_manager.run_task("continue_interview", {
        "task_type": "continue_interview",
        "email": email,
        "qa_history": qa_history
    })

    if isinstance(next_q, dict) and "error" in next_q:
        return jsonify({"success": False, "message": next_q["error"]}), 500

    next_question_text = next_q if isinstance(next_q, str) else str(next_q)
    return jsonify({"success": True, "next_question": next_question_text})


@app.route('/complete_interview', methods=['POST'])
def complete_interview():
    try:
        content = request.json
        email = content.get("email")
        qa_history = content.get("qa_history", [])

        if not email:
            return jsonify({"success": False, "message": "Missing email"}), 400

        completed_qa = task_manager.run_task("conduct_full_interview", {"email": email, "qa_history": qa_history})
        if isinstance(completed_qa, str):
            return jsonify({"success": False, "message": completed_qa}), 500

        if not all(q.get("answer", "").strip() for q in completed_qa):
            return jsonify({"success": False, "message": "Some answers are missing."}), 400

        evaluation = task_manager.run_task("evaluate_interview", {"email": email, "qa_history": completed_qa})
        if "error" in evaluation:
            return jsonify({"success": False, "message": evaluation["error"], "raw": evaluation.get("raw_response", "")}), 500

        return jsonify({
            "success": True,
            "interview": evaluation.get("questions", []),
            "score": evaluation.get("total_score"),
            "feedback": evaluation.get("overall_feedback")
        })

    except Exception:
        tb = traceback.format_exc()
        print("Error in /complete_interview:", tb)
        return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/trigger')
def trigger_page():
    return render_template('trigger_pipeline.html')

@app.route('/extract')
def extract_page():
    return render_template('extract_profile.html')

@app.route('/emails')
def emails_page():
    return render_template('generate_emails.html')

@app.route('/interview')
def interview_page():
    return render_template('interview.html')

if __name__ == '__main__':
    # Bind to 0.0.0.0 so the app is reachable from other machines (VPS host/network)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
