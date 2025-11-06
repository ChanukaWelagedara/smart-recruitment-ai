from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config.langchain_config import LangChainConfig
from agents.base_agent import BaseAgent

class LangChainEmailGenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__("email_generation_agent")
        self.llm = LangChainConfig.get_llm()

        self.email_prompt = PromptTemplate(
            input_variables=[
                "job_description",
                "interview_date",
                "candidate_name",
                "candidate_email",
                "job_title",
                "closing_date",
                "company_name",
                "contact_info"
            ],
            template="""
You are an HR assistant writing a professional email from the company to the candidate regarding their job application.

Use the following details:

Job Title: {job_title}
Job Description: {job_description}
Interview Date: {interview_date}
Application Closing Date: {closing_date}
Candidate Name: {candidate_name}
Candidate Email: {candidate_email}
Company Name: {company_name}
Contact Information: {contact_info}

Write a formal recruitment email inviting the candidate to an interview on {interview_date}.

Include:
- A polite greeting
- Confirmation of the interview date and position applied for
- Brief instructions or next steps for the candidate to prepare
- Contact information for questions
- A professional closing

Write the email as if it is sent by the Hiring Manager or HR team.

Format the email with a subject line and a professional body.

Subject: Interview Invitation for {job_title} Position

Dear {candidate_name},

[Email body]

Best regards,
Hiring Manager
{company_name}
{contact_info}

Generate the complete email below:
"""
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.email_prompt)

    def can_handle(self, task_type: str) -> bool:
        return task_type == "send_email"

    def perform_task(self, data: dict, context: dict = None):
        try:
            return self.chain.run(
                job_description=data["job_description"],
                interview_date=data["interview_date"],
                candidate_name=data["candidate_name"],
                candidate_email=data["candidate_email"],
                job_title=data["job_title"],
                closing_date=data["closing_date"],
                company_name=data["company_name"],
                contact_info=data["contact_info"],
                
            )
        except Exception as e:
            return f"Error generating email: {str(e)}"
