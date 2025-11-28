from .base_agent import BaseAgent
from config.langchain_config import LangChainConfig

class GeneralInterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("GeneralInterviewAgent")
        self.llm = LangChainConfig.get_llm()
        self.max_questions = 5

    def can_handle(self, task_type: str) -> bool:
        return task_type in ["start_general_interview", "answer_general"]

    def perform_task(self, data: dict, context: dict = None):
        task_type = data.get("task_type")
        qa_history = data.get("qa_history", [])

        # ---------------- START INTERVIEW ----------------
        if task_type == "start_general_interview":
            prompt = (
    "You are an HR interviewer starting a soft-skills interview. "
    "Ask the first question in a natural, conversational flow. "
    "Start with a warm, friendly, introductory question (e.g., background, personal story, interests). "
    "Keep it short, human-like, and non-technical."
)
            try:
                ai_message = self.llm.invoke(prompt)
                first_question = ai_message.content.strip()
                if not first_question:
                    first_question = "Tell me about yourself."
            except Exception:
                first_question = "Tell me about yourself."

            return {"success": True, "question": first_question}

        # ---------------- ANSWER GENERAL ----------------
        elif task_type == "answer_general":
            # If 5 questions already answered
            if len(qa_history) >= self.max_questions:
                return {
                    "success": True,
                    "finished": True,
                    "message": "General interview finished. Let's move on to technical questions."
                }

            # Generate next question dynamically
            history_text = "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in qa_history])
            prompt = (
            f"You are an HR interviewer conducting a soft-skills interview.\n"
            f"Here is the conversation so far:\n{history_text}\n\n"
            "Now ask the *next logical non-technical question* that follows the interview flow.\n"
            "Follow these rules:\n"
            "1. Do NOT repeat previous questions.\n"
            "2. Each question must naturally follow from the candidate's last answer.\n"
            "3. Keep it conversational, human-like, and short.\n"
            "4. Focus on personality, background, communication, teamwork, interests, goals, etc.\n"
            "Ask only ONE question."
        )


            try:
                ai_message = self.llm.invoke(prompt)
                next_question = ai_message.content.strip()
                if not next_question:
                    next_question = "Tell me something interesting about yourself."
            except Exception:
                next_question = "Tell me something interesting about yourself."

            return {"success": True, "question": next_question}

        return {"success": False, "message": "Unsupported task type"}
