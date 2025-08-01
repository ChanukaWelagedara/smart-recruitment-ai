from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from config.langchain_config import LangChainConfig

class LangChainEmailGenerationAgent:
    def __init__(self):
        self.llm = LangChainConfig.get_llm()

        self.email_prompt = PromptTemplate(
            input_variables=[
                "job_description",
                "interview_date",
                "candidate_name",
                "candidate_email",
                "job_title",
                "closing_date"
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

Write a formal recruitment email inviting the candidate to an interview on the scheduled interview date.

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
[Company Name]
[Contact Information]

Generate the complete email below:
"""
        )

        self.chain = LLMChain(llm=self.llm, prompt=self.email_prompt)

    def generate_email(self, job_description, interview_date, candidate_name, candidate_email,
                       job_title, closing_date):
        try:
            return self.chain.run(
                job_description=job_description,
                interview_date=interview_date,
                candidate_name=candidate_name,
                candidate_email=candidate_email,
                job_title=job_title,
                closing_date=closing_date
            )
        except Exception as e:
            return f"Error generating email: {str(e)}"
