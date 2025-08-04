127.0.0.1 - - [03/Aug/2025 18:19:52] "POST /start_interview HTTP/1.1" 200 -
127.0.0.1 - - [03/Aug/2025 18:19:54] "GET / HTTP/1.1" 200 -
Looking for email: lithira.uthsara123@gmail.com. Available emails:
- lithira.uthsara123@gmail.com
127.0.0.1 - - [03/Aug/2025 18:19:57] "POST /start_interview HTTP/1.1" 200 -

this response is given and in ui AI Interview Chat
Email: 
lithira.uthsara123@gmail.com
 Start
Q: [object Object]
Type your answer...
 Send this is the Code 


import os
from database.langchain_vector_db import LangChainVectorDB
from utils.hash_utils import get_file_hash
from agents.langchain_job_matcher_agent import extract_match_score

class TaskManager:
    def __init__(self, agents):
        self.agents = agents

    def run_task(self, task_type: str, data: dict = None, context: dict = None):
        data = data or {}
        for agent in self.agents:
            if agent.can_handle(task_type):
                try:
                    return agent.perform_task(data, context)
                except Exception as e:
                    return {"error": f"Error in task '{task_type}' by agent '{agent.name}': {str(e)}"}
        return {"error": f"No agent found to handle task type: {task_type}"}

    def orchestrate_application(self, job_post: dict, candidates: list):
        vector_db = LangChainVectorDB()
        results = []

        existing_cv_summaries = vector_db.get_all_cv_summaries()
        hash_to_summary = {
            cv.get("metadata", {}).get("file_hash"): cv["text"]
            for cv in existing_cv_summaries
            if cv.get("metadata", {}).get("file_hash")
        }

        job_description = job_post.get("jobDescription", "")
        job_title = job_post.get("jobTitle", "Unknown Job")

        for candidate in candidates:
            full_name = f"{candidate.get('firstName', '')} {candidate.get('lastName', '')}"
            cv_url = candidate.get("cvURL")
            email = candidate.get("email", "unknown@example.com")

            if not cv_url:
                results.append({"candidate_name": full_name, "error": "No CV URL"})
                continue

            download_result = self.run_task("download_file", {
                "url": cv_url,
                "filename": cv_url.split("/")[-1]
            })

            if "error" in download_result:
                results.append({"candidate_name": full_name, "error": download_result["error"]})
                continue

            local_cv_path = download_result.get("file_path")
            if not local_cv_path or not os.path.exists(local_cv_path):
                results.append({"candidate_name": full_name, "error": "Downloaded file missing"})
                continue

            file_hash = get_file_hash(local_cv_path)
            if file_hash in hash_to_summary:
                cv_summary = hash_to_summary[file_hash]
            else:
                summary_result = self.run_task("summarize_cv", {"cv_path": local_cv_path})
                if isinstance(summary_result, dict) and "error" in summary_result:
                    results.append({"candidate_name": full_name, "error": summary_result["error"]})
                    continue
                cv_summary = summary_result
                vector_db.add_text_document(
                    text=cv_summary,
                    doc_id=email,
                    doc_type="cv_summary",
                    file_hash=file_hash,
                    email=email
                )
                hash_to_summary[file_hash] = cv_summary

            safeguard_result = self.run_task("safeguard_data_check", {"candidate_data": candidate})
            if "error" in safeguard_result:
                results.append({"candidate_name": full_name, "error": safeguard_result["error"]})
                continue

            match_result = self.run_task("match_cv", {"cv_summary": cv_summary, "job_summary": job_description})
            score = extract_match_score(match_result) if isinstance(match_result, str) else 0

            email_result = self.run_task("send_email", {
                "cv_summary": cv_summary,
                "job_summary": job_description,
                "candidate_email": email,
                "candidate_name": full_name,
                "job_title": job_title,
                "closing_date": job_post.get("closingDate", "")
            })

            results.append({
                "candidate_name": full_name,
                "email": email,
                "score": score,
                "match_analysis": match_result,
                "email_content": email_result
            })

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results



import json
from database.langchain_vector_db import LangChainVectorDB
from config.langchain_config import LangChainConfig
from agents.base_agent import BaseAgent

class LangChainInterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("interview_agent")
        self.db = LangChainVectorDB()
        self.llm = LangChainConfig.get_llm()

    def can_handle(self, task_type: str) -> bool:
        # Define task types this agent handles
        return task_type in {
            "start_interview",
            "continue_interview",
            "conduct_full_interview",
            "evaluate_interview"
        }

    def perform_task(self, data: dict, context: dict = None):
        task_type = data.get("task_type")
        email = data.get("email")
        if not email:
            return {"error": "Missing candidate email"}

        cv_summary = self.db.get_cv_summary_by_email(email)
        if not cv_summary:
            return {"error": f"No CV summary found for email: {email}"}

        if task_type == "start_interview":
            return self._start_interview(cv_summary)

        elif task_type == "continue_interview":
            qa_history = data.get("qa_history", [])
            return self._continue_interview(cv_summary, qa_history)

        elif task_type == "conduct_full_interview":
            qa_history = data.get("qa_history", [])
            return self._conduct_full_interview(cv_summary, qa_history)

        elif task_type == "evaluate_interview":
            qa_history = data.get("qa_history", [])
            return self._evaluate_interview(cv_summary, qa_history)

        else:
            return {"error": f"Unknown task type: {task_type}"}

    def _invoke_llm(self, prompt: str) -> str:
        try:
            if hasattr(self.llm, 'invoke'):
                response = self.llm.invoke(prompt)
                return response.content.strip() if hasattr(response, 'content') else response.strip()
            else:
                response = self.llm(prompt)
                return response.content.strip() if hasattr(response, 'content') else response.strip()
        except Exception as e:
            return f"Error invoking LLM: {str(e)}"

    def _start_interview(self, cv_summary: str) -> str:
        prompt = f"""
You are an expert technical interviewer. Your job is to generate the first interview question based on the candidate's CV.

CV Summary:
\"\"\"
{cv_summary}
\"\"\"

Start by asking a relevant web development interview question, based on the technologies mentioned (e.g., MERN stack, Node.js, MongoDB).
Only return the question.
"""
        return self._invoke_llm(prompt)

    def _continue_interview(self, cv_summary: str, qa_history: list) -> str:
        history_str = ""
        for i, pair in enumerate(qa_history, 1):
            q = pair.get("question", "")
            a = pair.get("answer", "")
            history_str += f"Q{i}: {q}\nA{i}: {a}\n"

        prompt = f"""
You are an expert technical interviewer continuing an interview with a web developer.

Here’s the candidate’s CV Summary:
\"\"\"
{cv_summary}
\"\"\"

Here is the conversation so far:
{history_str}

Now, based on the candidate's last answer, ask the **next technical question**. Go deeper into reasoning, architecture, tools, deployment, etc.
Only return the question text.
"""
        return self._invoke_llm(prompt)

    def _conduct_full_interview(self, cv_summary: str, qa_history: list) -> list:
        full_qa = qa_history.copy()

        for _ in range(5 - len(full_qa)):
            history_str = ""
            for i, pair in enumerate(full_qa, 1):
                q = pair.get("question", "").strip()
                a = pair.get("answer", "").strip()
                history_str += f"Q{i}: {q}\nA{i}: {a}\n"

            prompt = f"""
You are an expert technical interviewer continuing an interview with a web developer.

Here’s the candidate’s CV Summary:
\"\"\"{cv_summary}\"\"\"

Here is the conversation so far:
{history_str}

Now, based on the candidate's last answer, ask the **next technical question**.
Make sure the question is technical, relevant to web development, and progressively deeper in complexity.
Only return the question text.
"""
            question = self._invoke_llm(prompt)
            full_qa.append({"question": question, "answer": ""})

        return full_qa

    def _evaluate_interview(self, cv_summary: str, qa_history: list) -> dict:
        history_str = ""
        for i, pair in enumerate(qa_history, 1):
            q = pair.get("question", "").strip()
            a = pair.get("answer", "").strip()
            history_str += f"Q{i}: {q}\nA{i}: {a}\n"

        prompt = f"""
You are a senior technical interviewer.

The following is a completed technical interview with a web developer candidate.

Candidate CV Summary:
\"\"\"{cv_summary}\"\"\"

Interview Transcript:
{history_str}

Evaluate each individual answer. For each of the 5 questions, assign:
- "question": the question asked
- "answer": the candidate's answer
- "score": a number out of 20
- "feedback": 1-2 sentences of feedback on that specific answer

Then, also include:
- "total_score": a number out of 100 (sum of the individual scores)
- "overall_feedback": a 2-3 sentence summary of the candidate's performance

Return ONLY a valid JSON object exactly like this, with NO extra explanation or commentary:

{{
"questions": [
    {{"question": "...", "answer": "...", "score": 18, "feedback": "..."}},
    ...
],
"total_score": 84,
"overall_feedback": "..."
}}
"""
        try:
            response_str = self._invoke_llm(prompt)
            # Debug print for raw output
            print("LLM raw evaluation response:", repr(response_str))
            evaluation_json = json.loads(response_str)
            return evaluation_json
        except Exception as e:
            return {
                "error": f"Error evaluating interview: {str(e)}",
                "raw_response": response_str if 'response_str' in locals() else None
            }
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

# Setup agents
existing_agents = [
    LangChainCVSummaryAgent(),
    LangChainJobMatcherAgent(),
    LangChainInterviewAgent(),
    LangChainEmailGenerationAgent(),
    LangChainCVInfoExtractorAgent(),
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

    question = task_manager.run_task("start_interview", {"email": email})
    return jsonify({"success": True, "question": question})

@app.route('/next_question', methods=['POST'])
def next_question():
    content = request.json
    email = content.get("email")
    qa_history = content.get("qa_history", [])

    if not email or not qa_history:
        return jsonify({"success": False, "message": "Missing email or qa_history"}), 400

    next_q = task_manager.run_task("next_question", {"email": email, "qa_history": qa_history})
    return jsonify({"success": True, "next_question": next_q})

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
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5000, debug=True)

why questionas ate not in here 