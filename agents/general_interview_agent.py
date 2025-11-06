from .base_agent import BaseAgent
from config.langchain_config import LangChainConfig
import random

class GeneralInterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("GeneralInterviewAgent")
        self.llm = LangChainConfig.get_llm()
        self.base_prompt = (
            "Generate 5 general interview questions for a candidate. "
            "Questions should be non-technical and related to background, motivation, experience, or goals. "
            "Return each question on a new line starting with a dash (-)."
        )
        self.sessions = {}

    def can_handle(self, task_type: str) -> bool:
        return task_type in ["start_general_interview", "answer_general", "terminate_general"]

    def perform_task(self, data: dict, context: dict = None):
        task_type = data.get("task_type")
        email = data.get("email")

        if task_type == "start_general_interview":
            ai_message = self.llm.invoke(self.base_prompt)        
            questions_text = ai_message.content                   
            questions = self._extract_questions(questions_text)  
            self.sessions[email] = {
                "questions": questions,
                "answers": [],
                "current_index": 0,
                "completed": False
            }
            return {"success": True, "question": questions[0]}

        elif task_type == "answer_general":
            session = self.sessions.get(email)
            if not session:
                return {"success": False, "message": "Session not found."}
            if session.get("completed"):
                return {"success": False, "message": "Interview already completed."}
            
            session["answers"].append(data.get("answer"))
            session["current_index"] += 1
            if session["current_index"] < len(session["questions"]):
                return {"success": True, "next_question": session["questions"][session["current_index"]]}
            else:
                session["completed"] = True
                return {"success": True, "finished": True, "message": "General interview completed."}

        elif task_type == "terminate_general":
            session = self.sessions.pop(email, None)
            if not session:
                return {"success": False, "message": "No active interview session found to terminate."}
            session["completed"] = True
            return {"success": True, "message": "General interview terminated successfully."}

        return {"success": False, "message": "Unsupported task type"}

    def _extract_questions(self, text: str) -> list:
        # Assumes output is like: "- Question 1\n- Question 2\n..."
        return [q.strip("- ").strip() for q in text.strip().split("\n") if q.strip()]

# from .base_agent import BaseAgent
# from config.langchain_config import LangChainConfig
# import random

# class GeneralInterviewAgent(BaseAgent):
#     def __init__(self):
#         super().__init__("GeneralInterviewAgent")
#         self.llm = LangChainConfig.get_llm()
#         self.base_prompt = (
#             "Generate 5 general interview questions for a candidate. "
#             "Questions should be non-technical and related to background, motivation, experience, or goals. "
#             "Return each question on a new line starting with a dash (-)."
#         )
#         self.sessions = {}

#     def can_handle(self, task_type: str) -> bool:
#         return task_type in ["start_general_interview", "answer_general"]

#     def perform_task(self, data: dict, context: dict = None):
#         task_type = data.get("task_type")
#         email = data.get("email")

#         if task_type == "start_general_interview":
#             ai_message = self.llm.invoke(self.base_prompt)        
#             questions_text = ai_message.content                   
#             questions = self._extract_questions(questions_text)  
#             self.sessions[email] = {
#                 "questions": questions,
#                 "answers": [],
#                 "current_index": 0
#             }
#             return {"success": True, "question": questions[0]}

#         elif task_type == "answer_general":
#             session = self.sessions.get(email)
#             if not session:
#                 return {"success": False, "message": "Session not found."}
#             session["answers"].append(data.get("answer"))
#             session["current_index"] += 1
#             if session["current_index"] < len(session["questions"]):
#                 return {"success": True, "next_question": session["questions"][session["current_index"]]}
#             else:
#                 session["completed"] = True
#                 return {"success": True, "finished": True}

#         return {"success": False, "message": "Unsupported task type"}

#     def _extract_questions(self, text: str) -> list:
#         # Assumes output is like: "- Question 1\n- Question 2\n..."
#         return [q.strip("- ").strip() for q in text.strip().split("\n") if q.strip()]
