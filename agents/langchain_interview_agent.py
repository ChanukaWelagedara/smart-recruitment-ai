import json
from database.langchain_vector_db import LangChainVectorDB
from config.langchain_config import LangChainConfig

class LangChainInterviewAgent:
    def __init__(self):
        self.db = LangChainVectorDB()
        self.llm = LangChainConfig.get_llm()

    def start_interview(self, email: str):
        cv_summary = self.db.get_cv_summary_by_email(email)
        if not cv_summary:
            return f"No CV summary found for email: {email}"

        prompt = f"""
You are an expert technical interviewer. Your job is to generate the first interview question based on the candidate's CV.

CV Summary:
\"\"\"
{cv_summary}
\"\"\"

Start by asking a relevant web development interview question, based on the technologies mentioned (e.g., MERN stack, Node.js, MongoDB).
Only return the question.
"""
        try:
            response = self.llm.invoke(prompt) if hasattr(self.llm, 'invoke') else self.llm(prompt)
            return response.content.strip() if hasattr(response, 'content') else response.strip()
        except Exception as e:
            return f"Error starting interview: {str(e)}"

    def continue_interview(self, email: str, qa_history: list):
        cv_summary = self.db.get_cv_summary_by_email(email)
        if not cv_summary:
            return f"No CV summary found for email: {email}"

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

        try:
            response = self.llm.invoke(prompt) if hasattr(self.llm, 'invoke') else self.llm(prompt)
            return response.content.strip() if hasattr(response, 'content') else response.strip()
        except Exception as e:
            return f"Error generating next question: {str(e)}"

    def conduct_full_interview(self, email: str, qa_history: list):
        cv_summary = self.db.get_cv_summary_by_email(email)
        if not cv_summary:
            return f"No CV summary found for email: {email}"

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

            try:
                response = self.llm.invoke(prompt) if hasattr(self.llm, 'invoke') else self.llm(prompt)
                question = response.content.strip() if hasattr(response, 'content') else response.strip()
                full_qa.append({"question": question, "answer": ""})
            except Exception as e:
                return f"Error generating question: {str(e)}"

        return full_qa

    def evaluate_interview(self, email: str, qa_history: list):
            cv_summary = self.db.get_cv_summary_by_email(email)
            if not cv_summary:
                return {"error": f"No CV summary found for email: {email}"}

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
                response = self.llm.invoke(prompt) if hasattr(self.llm, 'invoke') else self.llm(prompt)
                evaluation_str = response.content.strip() if hasattr(response, 'content') else response.strip()

                # DEBUG: print raw output from LLM
                print("LLM raw evaluation response:", repr(evaluation_str))

                # Parse JSON string returned by LLM
                evaluation_json = json.loads(evaluation_str)

                return evaluation_json

            except Exception as e:
                print(f"Error evaluating interview JSON parsing: {e}")
                print("Raw evaluation string was:", repr(evaluation_str))
                return {"error": f"Error evaluating interview: {str(e)}", "raw_response": evaluation_str}