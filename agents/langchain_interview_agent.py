import json
import uuid
from database.langchain_vector_db import LangChainVectorDB
from config.langchain_config import LangChainConfig
from agents.base_agent import BaseAgent

class LangChainInterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("interview_agent")
        self.db = LangChainVectorDB()
        self.llm = LangChainConfig.get_llm()
        self.sessions = {}

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
        job_description = data.get("job_description", "")
        qa_history = data.get("qa_history", [])
        violations = data.get("violations", [])
        if not email:
            return {"error": "Missing candidate email"}

        cv_summary = self.db.get_cv_summary_by_email(email)
        if not cv_summary:
            return {"error": f"No CV summary found for email: {email}"}
        
        if email not in self.sessions:
            self.sessions[email] = {
               
                "cv_summary": cv_summary,
                "job_description": job_description,
                "qa_history": [],
                "violations": []
            }
        session = self.sessions[email]

        if task_type == "start_interview":
            first_question = self._start_interview(cv_summary, job_description)
            session["qa_history"].append({"question": first_question, "answer": ""})
            return {"question": first_question}

        elif task_type == "continue_interview":
            # Save previous answer if present
            if qa_history:
                session["qa_history"] = qa_history
            
            if violations :
                session.setdefault("violations", []).extend(violations)

            if len(session["qa_history"]) >= 5:
                evaluation = self._evaluate_interview(
                    session["cv_summary"], 
                    session["qa_history"],
                    session.get("violations", [])
                )

                self.sessions.pop(email, None)

                return {
                    "success": True,
                    "finished": True,
                    "message": "Thank you for completing the technical interview!",
                    "qa_history": session["qa_history"],
                    "violations": session.get("violations", []),
                    "evaluation": {
                        "total_score": evaluation.get("total_score"),
                        "overall_feedback": evaluation.get("overall_feedback"),
                        "question_wise": evaluation.get("questions", [])
                    }
                }

            # Otherwise, continue with next question
            next_question = self._continue_interview(session["cv_summary"], session["qa_history"])
            return {
                "success": True,
                "next_question": next_question,
                "qa_history": session["qa_history"],
                "violations": session.get("violations", [])
            }



        elif task_type == "conduct_full_interview":
            full_qa = self._conduct_full_interview(cv_summary, qa_history)
            return full_qa

        elif task_type == "evaluate_interview":
            evaluation = self._evaluate_interview(cv_summary, qa_history)
            return evaluation

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

    def _start_interview(self, cv_summary: str, job_description: str="") -> str:
        prompt = f"""
You are an expert technical interviewer. 
Your goal is to generate the first **technical question** for a candidate applying for this role.
Carefully analyze the following information:
CV Summary:
\"\"\"
{cv_summary}
\"\"\"

Job Description:
\"\"\"{job_description}\"\"\"
**Instructions:**
1. First, identify key **skills, technologies, and responsibilities** mentioned in the job post (e.g., MERN, APIs, React, AWS, CI/CD).
2. Then, read the CV summary and find the **most relevant experience or skills** that match the job requirements.
3. Based on this overlap, generate **one strong technical question** that:
   - Tests the candidate’s real understanding or problem-solving skills.
   - Is relevant to both the job and the candidate’s CV.
   - Is phrased clearly and professionally.
   - Focuses on reasoning, system design, or applied technical skill (not trivia).

**Example Output:**
- "Can you explain how you optimized a MongoDB query for scalability in one of your past MERN projects?"
- "In your experience deploying React and Node.js applications, what challenges did you face with AWS or CI/CD pipelines?"
Only return the question text — no explanation or commentary.
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

        for _ in range(6 - len(full_qa)):
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
    
    # def _evaluate_interview(self, cv_summary: str, qa_history: list, violations: list = None) -> dict:
    #     qa_history = qa_history or []
    #     violations = violations or []

    #     history_str = ""
    #     for i, pair in enumerate(qa_history, 1):
    #         q = pair.get("question", "").strip()
    #         a = pair.get("answer", "").strip()
    #         history_str += f"Q{i}: {q}\nA{i}: {a}\n"

    #     violations_str = ""
    #     if violations:
    #         for v in violations:
    #             violations_str += f"- {v.get('name', '')} at {v.get('timestamp', '')}\n"

    #     prompt = f"""
    #     You are a senior technical interviewer.
    #     Candidate CV Summary:
    #     \"\"\"{cv_summary}\"\"\"
    #     Interview Transcript:
    #     {history_str}
    #     Behavioral Violations:
    #     {violations_str if violations_str else 'None'}
    #     Evaluate each individual answer. For each question, assign:
    #     - "question": the question asked
    #     - "answer": the candidate's answer
    #     - "score": a number out of 20
    #     - "feedback": 1-2 sentences of feedback
    #     - "masked": false
    #     Include the violations as-is.
    #     Also include:
    #     - "total_score": sum of individual scores
    #     - "overall_feedback": 2-3 sentence summary of candidate's performance
    #     Return ONLY a valid JSON object exactly like this:
    #     {{
    #     "questions": [
    #         {{"question": "...", "answer": "...", "score": 18, "feedback": "...", "masked": false}},
    #         ...
    #     ],
    #     "violations": {violations},
    #     "total_score": 84,
    #     "overall_feedback": "..."
    #     }}
    #     """

    #     try:
    #         response_str = self._invoke_llm(prompt)
    #         cleaned = response_str.replace("```json", "").replace("```", "").strip()
    #         evaluation_json = json.loads(cleaned)

    #         # Ensure required keys exist, but do NOT overwrite LLM feedback/scores
    #         evaluation_json.setdefault("questions", [])
    #         evaluation_json.setdefault("question_wise", evaluation_json.get("questions", []))
    #         evaluation_json.setdefault("violations", violations)
    #         evaluation_json.setdefault(
    #             "total_score", 
    #             sum(q.get("score", 0) for q in evaluation_json["questions"])
    #         )
    #         evaluation_json.setdefault(
    #             "overall_feedback",
    #             f"{len(violations)} violations recorded. Candidate performance considered."
    #         )

    #     except Exception as e:
    #         # Only run fallback if LLM completely fails
    #         num_questions = len(qa_history)
    #         deduction_per_violation = 2
    #         total_deduction = deduction_per_violation * len(violations) * num_questions

    #         questions_list = []
    #         for q in qa_history:
    #             questions_list.append({
    #                 "question": q.get("question", ""),
    #                 "answer": q.get("answer", ""),
    #                 "score": max(0, 20 - deduction_per_violation * len(violations)),
    #                 "feedback": "Auto-evaluated",
    #                 "masked": False
    #             })

    #         evaluation_json = {
    #             "questions": questions_list,
    #             "question_wise": questions_list,
    #             "violations": violations,
    #             "total_score": max(0, 20 * num_questions - total_deduction),
    #             "overall_feedback": f"{len(violations)} violations recorded. Candidate performance considered."
    #         }

    #     return evaluation_json

    # def _evaluate_interview(self, cv_summary: str, qa_history: list, violations: list = None) -> dict:
    #     qa_history = qa_history or []
    #     violations = violations or []

    #     # Build history string for LLM prompt
    #     history_str = ""
    #     for i, pair in enumerate(qa_history, 1):
    #         q = pair.get("question", "").strip()
    #         a = pair.get("answer", "").strip()
    #         history_str += f"Q{i}: {q}\nA{i}: {a}\n"

    #     # Build violations string
    #     violations_str = ""
    #     if violations:
    #         for v in violations:
    #             violations_str += f"- {v.get('name', '')} at {v.get('timestamp', '')}\n"

    #     # LLM prompt
    #     prompt = f"""
    # You are a senior technical interviewer.

    # Candidate CV Summary:
    # \"\"\"{cv_summary}\"\"\"

    # Interview Transcript:
    # {history_str}

    # Behavioral Violations:
    # {violations_str if violations_str else 'None'}

    # Evaluate each individual answer. For each question, assign:
    # - "question": the question asked
    # - "answer": the candidate's answer
    # - "score": a number out of 20
    # - "feedback": 1-2 sentences of feedback
    # - "masked": false

    # Include the violations as-is.

    # Also include:
    # - "total_score": sum of individual scores
    # - "overall_feedback": 2-3 sentence summary of candidate's performance

    # Return ONLY a valid JSON object exactly like this:

    # {{
    # "questions": [
    #     {{"question": "...", "answer": "...", "score": 18, "feedback": "...", "masked": false}},
    #     ...
    # ],
    # "violations": {violations},
    # "total_score": 84,
    # "overall_feedback": "..."
    # }}
    # """

    #     try:
    #         # Call LLM
    #         response_str = self._invoke_llm(prompt)
    #         print("LLM raw evaluation response:", repr(response_str))

    #         cleaned = (
    #             response_str.replace("```json", "")
    #             .replace("```", "")
    #             .strip()
    #         )

    #         # Try parsing LLM JSON
    #         evaluation_json = json.loads(cleaned)
    #         # Ensure keys exist
    #         evaluation_json.setdefault("questions", [])
    #         evaluation_json.setdefault("question_wise", evaluation_json.get("questions", []))
    #         evaluation_json.setdefault("violations", violations)
    #         evaluation_json.setdefault(
    #             "total_score", 
    #             sum(q.get("score", 0) for q in evaluation_json["questions"]))
    #         evaluation_json.setdefault(
    #             "overall_feedback",
    #             f"{len(violations)} violations recorded. Candidate performance considered."
    #         )

    #     except Exception as e:
    #         # Fallback if LLM fails
    #         print("LLM evaluation failed:", e)
    #         num_questions = len(qa_history)
    #         deduction_per_violation = 2
    #         total_deduction = deduction_per_violation * len(violations) * num_questions

    #         questions_list = []
    #         for q in qa_history:
    #             questions_list.append({
    #                 "question": q.get("question", ""),
    #                 "answer": q.get("answer", ""),
    #                 "score": max(0, 20 - deduction_per_violation * len(violations)),
    #                 "feedback": q.get("feedback", "Auto-evaluated"),
    #                 "masked": False
    #             })

    #         evaluation_json = {
    #             "questions": questions_list,
    #             "question_wise": questions_list,
    #             "violations": violations,
    #             "total_score": max(0, 20 * num_questions - total_deduction),
    #             "overall_feedback": f"{len(violations)} violations recorded. Candidate performance considered."
    #         }

    #     return evaluation_json


    def _evaluate_interview(self, cv_summary: str, qa_history: list, violations: list=None  ) -> dict:
        qa_history=qa_history or []
        violations=violations or []

        history_str = ""
        for i, pair in enumerate(qa_history, 1):
            q = pair.get("question", "").strip()
            a = pair.get("answer", "").strip()
            history_str += f"Q{i}: {q}\nA{i}: {a}\n"
        
        violations = violations or []
        violations_str=""
        if violations:
            for v in violations:
                violations_str+=f"- {v.get('name', '')} at {v.get('timestamp', '')}\n"

        prompt = f"""
You are a senior technical interviewer.

Candidate CV Summary:
\"\"\"{cv_summary}\"\"\"

Interview Transcript:
{history_str}

Behavioral Violations:
{violations_str if violations_str else 'None'}

Evaluate each individual answer. For each of the 5 questions, assign:
- "question": the question asked
- "answer": the candidate's answer
- "score": a number out of 20
- "feedback": 1-2 sentences of feedback on that specific answer
- "masked:false"
Also, include the violations list as-is.

Then, also include:
- "total_score": a number out of 100 (sum of the individual scores)
- "overall_feedback": a 2-3 sentence summary of the candidate's performance

Return ONLY a valid JSON object exactly like this, with NO extra explanation or commentary:

{{
"questions": [
    {{"question": "...", 
    "answer": "...", 
    "score": 18, 
    "feedback": "..."}},
    ...
],
"violations": {violations},
"total_score": 84,
"overall_feedback": "..."
}}
"""
        try:
            response_str = self._invoke_llm(prompt)
            print("LLM raw evaluation response:", repr(response_str))
            cleaned = (
                response_str.replace("```json", "")
                .replace("```", "")
                .replace("\n", "")
                .strip()
            )

            evaluation_json = json.loads(cleaned)

        except Exception as e:
            # Fallback: set default scores in case LLM fails or JSON parsing fails
            try:
                num_questions = len(qa_history)
                deduction_per_violation = 2
                total_deduction = deduction_per_violation * len(violations) * num_questions

                questions_list = []
                for q in qa_history:
                    feedback = q.get("feedback") or "Auto-evaluated"
                    score = max(0, 20 - deduction_per_violation * len(violations))
                   # score = max(0, 20 - deduction_per_violation * len(violations))
                    questions_list.append({
                        "question": q.get("question", ""),
                        "answer": q.get("answer", ""),
                        "score": 20,
                        "feedback":feedback,
                        "masked": False
                    })
                total_score = max(0, 20 * num_questions - total_deduction)

                evaluation_json = {
                    "questions": questions_list,
                    "question_wise": questions_list,
                    "violations": violations or [],
                    "total_score": total_score,
                    "overall_feedback": f"{len(violations)} violations recorded. Candidate performance considered."
                }

            except Exception as inner_e:
                # Last-resort: in case fallback itself fails
                evaluation_json = {
                    "error": f"Error evaluating interview: {str(inner_e)}",
                    "raw_response": response_str if 'response_str' in locals() else None,
                    "questions": [],
                    "question_wise": [],
                    "violations": violations or []
                }

            return evaluation_json

        # try:
        #     response_str = self._invoke_llm(prompt)
        #     print("LLM raw evaluation response:", repr(response_str))
        #     cleaned = (
        #         response_str.replace("```json", "")
        #         .replace("```", "")
        #         .replace("\n", "")
        #         .strip()
        #     )

        #     evaluation_json = json.loads(cleaned)
        # except Exception as e:
        # # Fallback: set default scores
        #     evaluation_json = {
        #         "questions": [{"question": q["question"], "answer": q["answer"], "score": max(0, 20 - 2*len(violations)), "feedback": "Auto-evaluated"} for q in qa_history],
        #         "violations": violations,
        #         "total_score": max(0, 100 - 2*len(violations)*len(qa_history)),  # Deduct 2 points per violation per question
        #         "overall_feedback": f"{len(violations)} violations recorded. Candidate performance considered.",
        #     }
        #     evaluation_json["questions"] = evaluation_json.get("questions", [])
        #     for q in evaluation_json["questions"]:
        #         q.setdefault("masked", False)
        #         q.setdefault("score", 0)
        #         q.setdefault("feedback", "")
        #     evaluation_json.setdefault("total_score", sum(q.get("score", 0) for q in evaluation_json["questions"]))
        #     evaluation_json.setdefault("overall_feedback", "Candidate performed well overall.")
        #     evaluation_json["question_wise"] = evaluation_json["questions"]
        #     evaluation_json["violations"]=violations or []
        #     return evaluation_json
        # except Exception as e:
        #     return {
        #         "error": f"Error evaluating interview: {str(e)}",
        #         "raw_response": response_str if 'response_str' in locals() else None,
        #         "questions": [],
        #         "question_wise": [],
        #         "violations": violations or []
        #     }