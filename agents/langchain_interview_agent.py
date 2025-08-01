# agents/langchain_interview_agent.py
from database.langchain_vector_db import LangChainVectorDB
from config.langchain_config import LangChainConfig

class LangChainInterviewAgent:
    def __init__(self):
        self.db = LangChainVectorDB()
        self.llm = LangChainConfig.get_llm()

    def generate_questions_from_summary(self, email: str):
        cv_summary = self.db.get_cv_summary_by_email(email)
        if not cv_summary:
            return f"No CV summary found for email: {email}"

        prompt = f"""
        The following is a professional summary of a candidate's CV:
        
        {cv_summary}

        Based on this summary, generate **5 personalized technical interview questions** across the following categories:
        1. Programming Languages
        2. Frameworks & Tools
        3. Database & Backend
        4. Deployment / Environments
        5. Software Engineering & Version Control

        The questions should be specific, challenging, and context-aware of the candidate's experience. Format them clearly using this example:

        1. Programming Languages (e.g., Java, Python, C#)
        "Question here"

        → 

        2. Frameworks & Tools (e.g., Vue.js, Laravel)
        "Question here"

        →

        Only return the questions.
        """

        try:
            if hasattr(self.llm, 'invoke'):
                from langchain_core.messages import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content.strip()
            else:
                return self.llm(prompt)  # fallback
        except Exception as e:
            return f"Error generating questions: {str(e)}"
