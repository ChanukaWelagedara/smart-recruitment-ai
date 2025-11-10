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
            prompt = f"Generate a short, non-technical interview question for a candidate. Keep it concise."
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
                f"Given the previous interview questions and answers:\n{history_text}\n"
                "Generate a new, short, non-technical interview question that is relevant and not repetitive."
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
