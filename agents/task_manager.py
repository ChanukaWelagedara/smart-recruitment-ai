import os
from database.langchain_vector_db import LangChainVectorDB
from utils.hash_utils import get_file_hash
from agents.langchain_job_matcher_agent import extract_match_score

class TaskManager:
    def __init__(self, agents):
        self.agents = agents

    def run_task(self, task_type: str, data: dict = None, context: dict = None):
        data = data or {}

        # Ensure 'task_type' key is present inside data for agent use
        if "task_type" not in data:
            data["task_type"] = task_type

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


# Helper function to run tasks via the global task_manager instance

def run_task(task_type: str, **kwargs):
   
    if "task_type" not in kwargs:
        kwargs["task_type"] = task_type
    return task_manager.run_task(task_type, kwargs)
