from .base_agent import BaseAgent
from config.langchain_config import LangChainConfig

class GeneralInterviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("GeneralInterviewAgent")
        self.llm = LangChainConfig.get_llm()
        self.default_question_count = 5  # Number of questions per interview
        # Fallback questions if LLM fails
        self.default_questions = [
            "Tell me about yourself.",
            "What motivates you?",
            "Describe a challenge you overcame.",
            "Where do you see yourself in 5 years?",
            "Why do you want this role?"
        ]

    def can_handle(self, task_type: str) -> bool:
        return task_type in ["start_general_interview", "answer_general"]

    def perform_task(self, data: dict, context: dict = None):
        task_type = data.get("task_type")
        qa_history = data.get("qa_history", [])

        # ---------------- START INTERVIEW ----------------
        if task_type == "start_general_interview":
            prompt = (
                f"Generate {self.default_question_count} short, non-technical interview questions. "
                "Return each question on a new line starting with '-'"
            )
            ai_message = self.llm.invoke(prompt)
            questions = [q.strip("- ").strip() for q in ai_message.content.split("\n") if q.strip()]

            if not questions or len(questions) < self.default_question_count:
                questions = self.default_questions

            return {
                "success": True,
                "question": questions[0],
                "all_questions": questions
            }

        # ---------------- ANSWER HANDLING ----------------
        elif task_type == "answer_general":
            questions = data.get("all_questions", self.default_questions)
            current_index = len(qa_history)

            if current_index < len(questions):
                # Return next question
                return {"success": True, "question": questions[current_index]}
            else:
                # All questions answered
                return {
                    "success": True,
                    "finished": True,
                    "message": "Now, let's move on to some technical questions."
                }

        return {"success": False, "message": "Unsupported task type"}

# from .base_agent import BaseAgent
# from config.langchain_config import LangChainConfig

# class GeneralInterviewAgent(BaseAgent):
#     def __init__(self):
#         super().__init__("GeneralInterviewAgent")
#         self.llm = LangChainConfig.get_llm()
#         self.default_question_count = 5  # Number of questions per interview
#         self.sessions = {}

#     def can_handle(self, task_type: str) -> bool:
#         return task_type in ["start_general_interview", "answer_general", "terminate_general"]

#     def perform_task(self, data: dict, context: dict = None):
#         task_type = data.get("task_type")
#         email = data.get("email")
#         qa_history = data.get("qa_history", [])

#         # ---------------- START INTERVIEW ----------------
#         if task_type == "start_general_interview":
#             prompt = (
#                 f"Generate {self.default_question_count} short, non-technical interview questions. "
#                 "Return each question on a new line starting with '-'"
#             )
#             ai_message = self.llm.invoke(prompt)
#             questions = [q.strip("- ").strip() for q in ai_message.content.split("\n") if q.strip()]
#             if not questions:
#                 questions = [f"Question #{i+1}" for i in range(self.default_question_count)]

#             # Save questions in session
#             self.sessions[email] = {
#                 "questions": questions,
#                 "completed": False
#             }

#             return {
#                 "success": True,
#                 "question": questions[0],
#                 "message": "General interview started."
#             }

#         # ---------------- ANSWER HANDLING ----------------
#         elif task_type == "answer_general":
#             session = self.sessions.get(email)
#             if not session:
#                 return {"success": False, "message": "Session not found."}

#             if session.get("completed"):
#                 return {
#                     "success": True,
#                     "finished": True,
#                     "message": "Now, let's move on to some technical questions."
#                 }

#             questions = session["questions"]
#             current_index = len(qa_history)

#             # All questions answered
#             if current_index >= len(questions):
#                 session["completed"] = True
#                 return {
#                     "success": True,
#                     "finished": True,
#                     "message": "Now, let's move on to some technical questions."
#                 }

#             # Return next question
#             next_q = questions[current_index]
#             return {
#                 "success": True,
#                 "question": next_q,
#                 "index": current_index + 1
#             }

#         # ---------------- TERMINATE INTERVIEW ----------------
#         elif task_type == "terminate_general":
#             self.sessions.pop(email, None)
#             return {"success": True, "message": "General interview terminated successfully."}

#         return {"success": False, "message": "Unsupported task type"}


# # agents/general_interview_agent.py
# from .base_agent import BaseAgent
# from config.langchain_config import LangChainConfig

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
#         return task_type in ["start_general_interview", "answer_general", "terminate_general"]

#     def perform_task(self, data: dict, context: dict = None):
#         task_type = data.get("task_type")
#         email = data.get("email")

#         # ---------------- START INTERVIEW ----------------
#         if task_type == "start_general_interview":
#             ai_message = self.llm.invoke(self.base_prompt)
#             questions_text = ai_message.content
#             questions = self._extract_questions(questions_text)

#             self.sessions[email] = {
#                 "questions": questions,
#                 "answers": [],
#                 "current_index": 0,
#                 "completed": False
#             }

#             return {
#                 "success": True,
#                 "question": questions[0],
#                 "message": "General interview started."
#             }

#         # ---------------- ANSWER HANDLING ----------------
#         elif task_type == "answer_general":
#             session = self.sessions.get(email)
#             if not session:
#                 return {"success": False, "message": "Session not found."}

#             if session.get("completed"):
#                 return {
#                     "success": True,
#                     "finished": True,
#                     "message": "Now, let's move on to some technical questions.!"
#                 }

#             # Save current answer
#             session["answers"].append(data.get("answer"))
#             session["current_index"] += 1

#             # Check if more questions remain
#             if session["current_index"] < len(session["questions"]):
#                 next_q = session["questions"][session["current_index"]]
#                 return {"success": True, "next_question": next_q}

#             # All questions answered
#             session["completed"] = True
#            # self.sessions.pop(email, None)
#             return {
#                 "success": True,
#                 "finished": True,
#                 "message": "Now, let's move on to some technical questions.!"
#             }

#         # ---------------- TERMINATE INTERVIEW ----------------
#         elif task_type == "terminate_general":
#             session = self.sessions.pop(email, None)
#             if not session:
#                 return {"success": False, "message": "No active interview session found to terminate."}
#             session["completed"] = True
#             return {"success": True, "message": "General interview terminated successfully."}

#         # ---------------- INVALID TASK ----------------
#         return {"success": False, "message": "Unsupported task type"}

#     def _extract_questions(self, text: str) -> list:
#         """Extracts questions from model response lines starting with '-'"""
#         return [q.strip("- ").strip() for q in text.strip().split("\n") if q.strip()]

# # from .base_agent import BaseAgent
# # from config.langchain_config import LangChainConfig
# # import random

# # class GeneralInterviewAgent(BaseAgent):
# #     def __init__(self):
# #         super().__init__("GeneralInterviewAgent")
# #         self.llm = LangChainConfig.get_llm()
# #         self.base_prompt = (
# #             "Generate {num_questions} general interview questions for a candidate. "
# #             "Questions should be non-technical and related to background, motivation, experience, or goals. "
# #             "Return each question on a new line starting with a dash (-)."
# #         )
# #         self.sessions = {}

# #     def can_handle(self, task_type: str) -> bool:
# #         return task_type in ["start_general_interview", "answer_general", "terminate_general"]

# #     def perform_task(self, data: dict, context: dict = None):
# #         task_type = data.get("task_type")
# #         email = data.get("email")
# #         num_questions = data.get("num_questions", 5) 

# #         # ---------------- START INTERVIEW ----------------
# #         if task_type == "start_general_interview":
# #             ai_message = self.llm.invoke(self.base_prompt)
# #             questions_text = ai_message.content
# #             questions = self._extract_questions(questions_text)

# #             self.sessions[email] = {
# #                 "questions": questions,
# #                 "answers": [],
# #                 "current_index": 0,
# #                 "completed": False
# #             }

# #             return {
# #                 "success": True,
# #                 "question": questions[0],
# #                 "message": "General interview started."
# #             }

# #         # ---------------- ANSWER HANDLING ----------------
# #         elif task_type == "answer_general":
# #             session = self.sessions.get(email)
# #             if not session:
# #                 return {"success": False, "message": "Session not found."}

# #             if session.get("completed"):
# #                 return {"success": False, "message": "Interview already completed."}

# #             # Save the current answer
# #             session["answers"].append(data.get("answer"))
# #             session["current_index"] += 1

# #             # Check if more questions remain
# #             if session["current_index"] < len(session["questions"]):
# #                 next_q = session["questions"][session["current_index"]]
# #                 return {"success": True, "next_question": next_q}

# #             # If all questions answered, end interview automatically
# #             session["completed"] = True
# #             self.sessions.pop(email, None)  # remove session after completion
# #             return {
# #                 "success": True,
# #                 "finished": True,
# #                 "message": "Your general interview is complete. Thank you for your responses!"
# #             }

# #         # ---------------- TERMINATE INTERVIEW ----------------
# #         elif task_type == "terminate_general":
# #             session = self.sessions.pop(email, None)
# #             if not session:
# #                 return {"success": False, "message": "No active interview session found to terminate."}

# #             session["completed"] = True
# #             return {"success": True, 
# #                     "message": "General interview terminated successfully."}

# #         # ---------------- INVALID TASK ----------------
# #         return {"success": False, "message": "Unsupported task type"}

# #     def _extract_questions(self, text: str) -> list:
# #         """Extracts questions from model response lines starting with '-'"""
# #         return [q.strip("- ").strip() for q in text.strip().split("\n") if q.strip()]


