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
            print("✅ Interview completed.")
            break
        elif next_response.get("next_question"):
            print(f"Q{i+2}: {next_response['next_question']}")

if __name__ == "__main__":
    simulate_interview()
