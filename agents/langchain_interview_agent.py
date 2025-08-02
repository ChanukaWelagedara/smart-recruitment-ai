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
            return self.llm.invoke(prompt).content.strip() if hasattr(self.llm, 'invoke') else self.llm(prompt)
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
            return self.llm.invoke(prompt).content.strip() if hasattr(self.llm, 'invoke') else self.llm(prompt)
        except Exception as e:
            return f"Error generating next question: {str(e)}"

