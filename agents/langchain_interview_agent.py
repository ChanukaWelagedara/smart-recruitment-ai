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
