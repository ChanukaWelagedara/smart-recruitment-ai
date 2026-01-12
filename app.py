from flask import Flask, request, jsonify, render_template
from datetime import datetime, timedelta
import traceback
from flask_cors import CORS 
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

# Initialize Task Manager
task_manager = TaskManager(all_agents)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# ---------------------------- PIPELINE ROUTES ---------------------------- #

@app.route('/trigger_pipeline', methods=['POST'])
def trigger_pipeline():
    try:
        content = request.json or {}
        data = content.get("data")
        if not data:
            return jsonify({"success": False, "message": "Missing application data"}), 400

        job_post = data.get("jobPost", {})
        candidates = data.get("candidateList", [])
        results = task_manager.orchestrate_application(job_post, candidates)

        return jsonify({"success": True, "results": results})
    except Exception:
        tb = traceback.format_exc()
        print("Error in /trigger_pipeline:", tb)
        return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500


@app.route('/extract_profile', methods=['POST'])
def extract_profile():
    try:
        content = request.json or {}
        cv_url = content.get("cvURL")
        if not cv_url:
            return jsonify({"success": False, "message": "Missing cvURL"}), 400

        result = task_manager.run_task("extract_profile_info", {"cv_url": cv_url})
        if result.get("error"):
            return jsonify({"success": False, "message": result["error"], "raw": result.get("raw_response", "")}), 500

        return jsonify({"success": True, "profile": result})
    except Exception:
        tb = traceback.format_exc()
        print("Error in /extract_profile:", tb)
        return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500


@app.route('/generate_emails', methods=['POST'])
def generate_emails():
    try:
        data = request.json or {}
        required_fields = ["jobId", "jobTitle", "jobDescription", "closingDate", "candidates", "companyName", "contactInfo"]
        for field in required_fields:
            if field not in data:
                return jsonify({"success": False, "message": f"Missing field: {field}"}), 400

        job_id = data["jobId"]
        job_title = data["jobTitle"]
        job_description = data["jobDescription"]
        closing_date_raw = data["closingDate"]
        candidates = data["candidates"]
        company_name = data["companyName"]
        contact_info = data["contactInfo"]

        # Parse closing date
        try:
            closing_date = datetime.fromisoformat(closing_date_raw.replace("Z", ""))
        except ValueError:
            return jsonify({"success": False, "message": "Invalid closingDate format"}), 400

        interview_date = data.get("interviewDate") or (closing_date + timedelta(days=7)).strftime('%Y-%m-%d')
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
                "closing_date": closing_date_str,
                "company_name": company_name,
                "contact_info": contact_info
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
            "company_name": company_name,
            "contact_info": contact_info,
            "emails": generated_emails
        })
    except Exception:
        tb = traceback.format_exc()
        print("Error in /generate_emails:", tb)
        return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500


@app.route('/generate_job_post', methods=['POST'])
def generate_job_post():
    try:
        data = request.json or {}
        required = ["job_title", "qualifications", "salary", "responsibilities"]
        missing = [r for r in required if not (data.get(r) or data.get(''.join([r.split('_')[0]] + [p.capitalize() for p in r.split('_')[1:]])))]
        if missing:
            return jsonify({"status": "error", "message": f"Missing fields: {', '.join(missing)}"}), 400

        result = task_manager.run_task("generate_job_post", {
            "job_title": data.get("job_title") or data.get("jobTitle"),
            "qualifications": data.get("qualifications"),
            "salary": data.get("salary"),
            "responsibilities": data.get("responsibilities")
        })

        if isinstance(result, dict):
            if result.get("status") == "error":
                return jsonify(result), 500
            elif result.get("status") == "success":
                return jsonify(result)

        return jsonify({"status": "success", "formatted_job_post": str(result)})
    except Exception:
        tb = traceback.format_exc()
        print("Error in /generate_job_post:", tb)
        return jsonify({"status": "error", "message": "Internal server error", "error": tb}), 500

@app.route('/start_interview', methods=['POST'])
def start_interview():
    try:
        content = request.json or {}
        email = content.get("email")
        job_description = content.get("job_description", "")

        if not email:
            return jsonify({"success": False, "message": "Missing email"}), 400

        # Use run_task instead of perform_task
        result = task_manager.run_task("start_interview", {
            "task_type": "start_interview",
            "email": email,
            "job_description": job_description,
            "violations":[]

        })

        if isinstance(result, dict) and "error" in result:
            return jsonify({"success": False, "message": result["error"]}), 500

        return jsonify({
            "success": True, 
            "question": str(result.get("question")),
            "violations":[]
            })
    except Exception:
        tb = traceback.format_exc()
        print("Error in /start_interview:", tb)
        return jsonify({
            "success": False, 
            "message": "Internal server error", 
            "error": tb}), 500

# @app.route('/next_question', methods=['POST'])
# def next_question():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         qa_history = content.get("qa_history", [])
#         violations = content.get("violations", [])

#         if not email:
#             return jsonify({"success": False, "message": "Missing email"}), 400

#         result = task_manager.run_task("continue_interview", {
#             "task_type": "continue_interview",
#             "email": email,
#             "qa_history": qa_history,
#             "violations": violations
#         })

#         if "error" in result:
#             return jsonify({"success": False, "message": result["error"]}), 500
#         if result.get("finished"):
#             evaluation = result.get("evaluation", {})
#             return jsonify({
#                 "success": True,
#                 "finished": True,
#                 "message": result.get("message"),
#                 "qa_history": result.get("qa_history", []),
#                 "violations": result.get("violations", []),
#                 "evaluation": {
#                     "total_score": evaluation.get("total_score", 0),
#                     "overall_feedback": evaluation.get("overall_feedback", "No feedback generated."),
#                     "question_wise": evaluation.get("question_wise", [])
#                 }
#             })


      
#         return jsonify({
#             "success": True,
#             "finished": False,
#             "next_question": result.get("next_question"),
#             "qa_history": result.get("qa_history", []),
#             "violations": result.get("violations", [])
#         })

#     except Exception as e:
#         tb = traceback.format_exc()
#         return jsonify({
#             "success": False,
#             "message": "Internal server error",
#             "error": str(e),
#             "trace": tb
#         }), 500

@app.route('/next_question', methods=['POST'])
def next_question():
    try:
        content = request.json or {}
        email = content.get("email")
        qa_history = content.get("qa_history", [])
        violations = content.get("violations", [])

        if not email:
            return jsonify({"success": False, "message": "Missing email"}), 400

        # Run the interview task
        result = task_manager.run_task("continue_interview", {
            "task_type": "continue_interview",
            "email": email,
            "qa_history": qa_history,
            "violations": violations
        })

        # Handle error from agent
        if "error" in result:
            return jsonify({"success": False, "message": result["error"]}), 500

        # If interview finished
        if result.get("finished"):
            evaluation = result.get("evaluation", {})
            
            # Directly use the LLM-generated feedback instead of placeholders
            return jsonify({
                "success": True,
                "finished": True,
                "message": result.get("message"),
                "qa_history": result.get("qa_history", []),
                "violations": result.get("violations", []),
                "evaluation": evaluation  # pass actual feedback here
            })

        # If interview not finished, return next question
        return jsonify({
            "success": True,
            "finished": False,
            "next_question": result.get("next_question"),
            "qa_history": result.get("qa_history", []),
            "violations": result.get("violations", [])
        })

    except Exception as e:
        tb = traceback.format_exc()
        return jsonify({
            "success": False,
            "message": "Internal server error",
            "error": str(e),
            "trace": tb
        }), 500

@app.route('/complete_interview', methods=['POST'])
def complete_interview():
    try:
        content = request.json or {}
        email, qa_history = content.get("email"), content.get("qa_history", [])
        if not email:
            return jsonify({"success": False, "message": "Missing email"}), 400

        completed_qa = task_manager.run_task("conduct_full_interview", {"email": email, "qa_history": qa_history})
        if isinstance(completed_qa, str):
            return jsonify({"success": False, "message": completed_qa}), 500

        if not all(q.get("answer", "").strip() for q in completed_qa):
            return jsonify({"success": False, "message": "Some answers are missing."}), 400

        evaluation = task_manager.run_task("evaluate_interview", {"email": email, "qa_history": completed_qa})
        if isinstance(evaluation, dict) and "error" in evaluation:
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
#---------------------------------------------------------------------#


# ---------------------------- GENERAL INTERVIEW ROUTES ---------------------------- #

@app.route('/start_general_interview', methods=['POST'])
def start_general_interview():
    try:
        content = request.json or {}
        email = content.get("email")
        if not email:
            return jsonify({"success": False, "message": "Missing email"}), 400

        result = task_manager.run_task("start_general_interview", {
            "task_type": "start_general_interview",
            "email": email,
            "qa_history": []
        })

        return jsonify({
            "success": True,
            "question": result.get("question"),
            "qa_history": [],
            "message": "General interview started."
        })

    except Exception:
        tb = traceback.format_exc()
        return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500


@app.route('/answer_general', methods=['POST'])
def answer_general():
    try:
        content = request.json or {}
        email = content.get("email")
        answer = content.get("answer")
        question = content.get("question")
        qa_history = content.get("qa_history", [])

        if not email or answer is None or not question:
            return jsonify({"success": False, "message": "Missing email, question, or answer"}), 400

        # Append current Q&A
        qa_history.append({"question": question, "answer": answer})

        # Stop after 5 questions
        if len(qa_history) >= 5:
            return jsonify({
                "success": True,
                "finished": True,
                "message": "General interview finished. Let's move on to technical questions.",
                "qa_history": qa_history
            })

        # Get next question from agent (LLM)
        result = task_manager.run_task("answer_general", {
            "task_type": "answer_general",
            "email": email,
            "qa_history": qa_history
        })

        return jsonify({
            "success": True,
            "question": result.get("question"),
            "qa_history": qa_history
        })

    except Exception:
        tb = traceback.format_exc()
        return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500


@app.route('/terminate_general', methods=['POST'])
def terminate_general():
    try:
        content = request.json or {}
        email = content.get("email")
        if not email:
            return jsonify({"success": False, "message": "Missing email"}), 400

        result = task_manager.run_task("terminate_general", {
            "task_type": "terminate_general",
            "email": email
        })
        return jsonify(result)
    except Exception:
        tb = traceback.format_exc()
        return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500

# ---------------------------- UI ROUTES ---------------------------- #

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

@app.route('/general_interview')
def general_interview_page():
    return render_template('general_interview.html')

# Health check endpoint for deployment monitoring
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "smart-recruitment-ai"
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

