# test_general_interview.py

from agents.general_interview_agent import GeneralInterviewAgent

def simulate_interview():
    agent = GeneralInterviewAgent()
    email = "test@example.com"

    # Start the general interview
    start_response = agent.perform_task({
        "task_type": "start_general_interview",
        "email": email
    })
    print(f"Q1: {start_response['question']}")
    
    # Loop through and simulate answering all questions
    for i in range(5):
        answer = input("Your answer: ")
        next_response = agent.perform_task({
            "task_type": "answer_general",
            "email": email,
            "answer": answer
        })

        if next_response.get("finished"):
            print("Interview completed.")
            break
        elif next_response.get("next_question"):
            print(f"Q{i+2}: {next_response['next_question']}")

if __name__ == "__main__":
    simulate_interview()

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


# @app.route('/start_general_interview', methods=['POST'])
# def start_general_interview():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         if not email:
#             return jsonify({"success": False, "message": "Missing email"}), 400

#         result = task_manager.run_task("start_general_interview", {
#             "task_type": "start_general_interview",
#             "email": email
#         })

#         return jsonify({
#             "success": True,
#             "question": result.get("question"),
#             "message": result.get("message", "Interview started.")
#         })
#     except Exception:
#         tb = traceback.format_exc()
#         return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500

# @app.route('/answer_general', methods=['POST'])
# def answer_general():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         answer = content.get("answer")
#         question = content.get("question")
#         qa_history = content.get("qa_history", [])

#         if not email or answer is None or not question:
#             return jsonify({"success": False, "message": "Missing email, question, or answer"}), 400

#         # Append latest Q&A to history
#         qa_history.append({"question": question, "answer": answer})

#         result = task_manager.run_task("answer_general", {
#             "task_type": "answer_general",
#             "email": email,
#             "qa_history": qa_history
#         })

#         # ---------------- FINISHED INTERVIEW ----------------
#         if result.get("finished"):
#             return jsonify({
#                 "success": True,
#                 "finished": True,
#                 "message": result.get("message", "Now, let's move on to some technical questions."),
#                 "qa_history": qa_history
#             })

#         # ---------------- NEXT QUESTION ----------------
#         next_question = result.get("question")
#         if next_question:
#             return jsonify({
#                 "success": True,
#                 "question": next_question,
#                 "index": result.get("index", len(qa_history) + 1),
#                 "qa_history": qa_history
#             })

#         # ---------------- FALLBACK ----------------
#         return jsonify({
#             "success": False,
#             "message": "Agent did not return a question",
#             "debug_result": str(result)
#         }), 500

#     except Exception:
#         tb = traceback.format_exc()
#         return jsonify({
#             "success": False,
#             "message": "Internal server error",
#             "error": tb
#         }), 500


# @app.route('/answer_general', methods=['POST'])
# def answer_general():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         answer = content.get("answer")
#         question = content.get("question")
#         qa_history = content.get("qa_history", [])

#         if not email or answer is None or not question:
#             return jsonify({"success": False, "message": "Missing email, question, or answer"}), 400

#         # Append latest Q&A to history
#         qa_history.append({"question": question, "answer": answer})

#         result = task_manager.run_task("answer_general", {
#             "task_type": "answer_general",
#             "email": email,
#             "qa_history": qa_history
#         })

#         if result.get("finished"):
#             return jsonify({
#                 "success": True,
#                 "finished": True,
#                 "message": result.get("message"),
#                 "qa_history": qa_history
#             })

#         return jsonify({
#             "success": True,
#             "question": result.get("question"),
#             "index": result.get("index", len(qa_history) + 1),
#             "qa_history": qa_history
#         })

#     except Exception:
#         tb = traceback.format_exc()
#         return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500

# @app.route('/start_general_interview', methods=['POST'])
# def start_general_interview():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         if not email:
#             return jsonify({"success": False, "message": "Missing email"}), 400

#         result = task_manager.run_task("start_general_interview", {
#             "task_type": "start_general_interview",
#             "email": email
#         })

#         if isinstance(result, dict) and not result.get("success"):
#             return jsonify(result), 500

#         return jsonify({
#             "success": True,
#             "question": result.get("question"),
#             "message": result.get("message", "Interview started.")
#         })
#     except Exception:
#         tb = traceback.format_exc()
#         return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500

# @app.route('/answer_general', methods=['POST'])
# def answer_general():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         answer = content.get("answer")

#         if not email or answer is None:
#             return jsonify({"success": False, "message": "Missing email or answer"}), 400

#         result = task_manager.run_task("answer_general", {
#             "task_type": "answer_general",
#             "email": email,
#             "answer": answer
#         })

#         if isinstance(result, dict) and result.get("finished"):
#             task_manager.run_task("terminate_general", {
#                 "task_type": "terminate_general",
#                 "email": email
#             })
#             return jsonify({
#                 "success": True,
#                 "finished": True,
#                 "message": result.get("message")
#             })

#         if isinstance(result, dict):
#             question_text = result.get("question") or result.get("next_question")
#             if question_text:
#                 return jsonify({"success": True, "question": question_text})
#             else:
#                 return jsonify({"success": False, "message": "Agent did not return a question"}), 500

#         return jsonify({"success": False, "message": "Unexpected response from agent"}), 500

#     except Exception:
#         tb = traceback.format_exc()
#         return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500

# @app.route('/answer_general', methods=['POST'])
# def answer_general():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         answer = content.get("answer")

#         if not email or answer is None:
#             return jsonify({"success": False, "message": "Missing email or answer"}), 400

#         # Call the agent via TaskManager
#         result = task_manager.run_task("answer_general", {
#             "task_type": "answer_general",
#             "email": email,
#             "answer": answer
#         })

#         # ------------------ CHECK IF INTERVIEW IS FINISHED ------------------
#         if isinstance(result, dict) and result.get("finished"):
#             # Optional: terminate session
#             task_manager.run_task("terminate_general", {
#                 "task_type": "terminate_general",
#                 "email": email
#             })
#             return jsonify({
#                 "success": True,
#                 "finished": True,
#                 "message": result.get("message", "General interview completed.")
#             })

#         # ------------------ ONGOING INTERVIEW ------------------
#         if isinstance(result, dict):
#             question_text = result.get("question") or result.get("next_question")
#             if question_text:
#                 return jsonify({"success": True, "question": question_text})
            
#             # No question returned
#             return jsonify({
#                 "success": False,
#                 "message": "Agent did not return a question",
#                 "debug_result": str(result)
#             }), 500

#         # ------------------ UNEXPECTED RESPONSE ------------------
#         return jsonify({
#             "success": False,
#             "message": "Unexpected response from interview agent",
#             "debug_type": str(type(result))
#         }), 500

#     except Exception:
#         tb = traceback.format_exc()
#         return jsonify({
#             "success": False,
#             "message": "Internal server error",
#             "error": tb
#         }), 500

# @app.route('/answer_general', methods=['POST'])
# def answer_general():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         answer = content.get("answer")

#         if not email or answer is None:
#             return jsonify({"success": False, "message": "Missing email or answer"}), 400

#         # Call the agent via TaskManager
#         result = task_manager.run_task("answer_general", {
#             "task_type": "answer_general",
#             "email": email,
#             "answer": answer
#         })

#         # ------------------ ONGOING INTERVIEW ------------------
#         if isinstance(result, dict):
#             # If interview is finished, return final message
#             if result.get("finished"):
#                 # Optional: terminate session
#                 task_manager.run_task("terminate_general", {
#                     "task_type": "terminate_general",
#                     "email": email
#                 })
#                 return jsonify({
#                     "success": True,
#                     "finished": True,
#                     "message": result.get("message", "Now, let's move on to some technical questions.")
#                 })

#             # If still ongoing, return next question
#             question_text = result.get("question") or result.get("next_question")
#             if question_text:
#                 return jsonify({"success": True, "question": question_text})

#             # Graceful fallback if no question returned
#             return jsonify({
#                 "success": False,
#                 "message": "Agent did not return a question",
#                 "debug_result": str(result)
#             }), 500

#         # ------------------ UNEXPECTED RESPONSE ------------------
#         return jsonify({
#             "success": False,
#             "message": "Unexpected response from interview agent",
#             "debug_type": str(type(result))
#         }), 500

#     except Exception:
#         tb = traceback.format_exc()
#         return jsonify({
#             "success": False,
#             "message": "Internal server error",
#             "error": tb
#         }), 500


# @app.route('/terminate_general', methods=['POST'])
# def terminate_general():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         if not email:
#             return jsonify({"success": False, "message": "Missing email"}), 400

#         result = task_manager.run_task("terminate_general", {
#             "task_type": "terminate_general",
#             "email": email
#         })
#         return jsonify(result)
#     except Exception:
#         tb = traceback.format_exc()
#         return jsonify({"success": False, "message": "Internal server error", "error": tb}), 500
# @app.route('/start_general_interview', methods=['POST'])
# def start_general_interview():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         num_questions = content.get("num_questions", 5)
#         if not email:
#             return jsonify({"success": False, "message": "Missing email"}), 400

#         result = task_manager.run_task("start_general_interview", {
#             "task_type": "start_general_interview",
#             "email": email,
#             "num_questions": num_questions
#         })

#         if isinstance(result, dict) and not result.get("success"):
#             return jsonify(result), 500

#         return jsonify({
#             "success": True,
#             "question": result.get("question"),
#             "message": result.get("message", "Interview started.")
#         })
#     except Exception:
#         tb = traceback.format_exc()
#         print("Error in /start_general_interview:", tb)
#         return jsonify({
#             "success": False,
#             "message": "Internal server error",
#             "error": tb
#         }), 500


# @app.route('/answer_general', methods=['POST'])
# def answer_general():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         answer = content.get("answer")

#         if not email or answer is None:
#             return jsonify({"success": False, "message": "Missing email or answer"}), 400

#         # Call the agent through TaskManager
#         result = task_manager.run_task("answer_general", {
#             "task_type": "answer_general",
#             "email": email,
#             "answer": answer
#         })

#         # Debug: Print what we got back
#         print(f"answer_general result for {email}:", result)
#         print(f"result type: {type(result)}")
       
#         if isinstance(result, dict) and result.get("finished"):
#             print(f"General interview completed for {email}")
#             print("Collected answers:")
#             # If the agent removed the session, you might store the answers in a DB later
#             # Here just print for now
#             print(result)

#             # Optionally call terminate to clean up (defensive safety)
#             task_manager.run_task("terminate_general", {
#                 "task_type": "terminate_general",
#                 "email": email
#             })

#             return jsonify({
#                 "success": True,
#                 "finished": True,
#                 "message": "Now, let's move on to some technical questions.!"
#             })

#         # If still ongoing, ensure we have a question to return
#         if isinstance(result, dict):
#             # Check for either 'question' or 'next_question' field
#             question_text = result.get("question") or result.get("next_question")
            
#             if question_text:
#                 # Normalize the response to always use 'question' field
#                 return jsonify({
#                     "success": result.get("success", True),
#                     "question": question_text
#                 })
#             else:
#                 # Missing question field - this is the problem!
#                 print(f"ERROR: No 'question' or 'next_question' field in result: {result}")
#                 return jsonify({
#                     "success": False,
#                     "message": "Agent did not return a question",
#                     "debug_result": str(result)
#                 }), 500
#         elif isinstance(result, str):
#             # If agent returned just a string, treat it as the question
#             return jsonify({"success": True, "question": result})
#         else:
#             print(f"ERROR: Unexpected result type: {type(result)}, value: {result}")
#             return jsonify({
#                 "success": False,
#                 "message": "Unexpected response from interview agent",
#                 "debug_type": str(type(result))
#             }), 500
#     except Exception:
#         tb = traceback.format_exc()
#         print("Error in /answer_general:", tb)
#         return jsonify({
#             "success": False,
#             "message": "Internal server error",
#             "error": tb
#         }), 500


# @app.route('/terminate_general', methods=['POST'])
# def terminate_general():
#     try:
#         content = request.json or {}
#         email = content.get("email")
#         if not email:
#             return jsonify({"success": False, "message": "Missing email"}), 400

#         result = task_manager.run_task("terminate_general", {
#             "task_type": "terminate_general",
#             "email": email
#         })
#         return jsonify(result)
#     except Exception:
#         tb = traceback.format_exc()
#         print("Error in /terminate_general:", tb)
#         return jsonify({
#             "success": False,
#             "message": "Internal server error",
#             "error": tb
#         }), 500
