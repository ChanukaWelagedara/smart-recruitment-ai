from .langchain_cv_summary_agent import LangChainCVSummaryAgent
from .langchain_job_matcher_agent import LangChainJobMatcherAgent
from .langchain_interview_agent import LangChainInterviewAgent
from .langchain_email_generation_agent import LangChainEmailGenerationAgent

# Initialize LangChain agents
cv_agent = LangChainCVSummaryAgent()
job_matcher = LangChainJobMatcherAgent()
interview_agent = LangChainInterviewAgent()
email_agent = LangChainEmailGenerationAgent()

def run_task(task_type, **kwargs):
    """Central task manager using LangChain agents"""
    try:
        if task_type == "summarize_cv":
            return cv_agent.summarize_cv(kwargs["cv_path"], kwargs.get("linkedin_url"))
        elif task_type == "match_cv":
            return job_matcher.match_cv_to_job(kwargs["cv_summary"], kwargs["job_summary"])
        elif task_type == "mcq_interview":
            return interview_agent.conduct_mcq_interview(kwargs["cv_summary"])
        elif task_type == "analyze_interview":
            return interview_agent.analyze_interview(kwargs["questions"], kwargs["answers"])
        elif task_type == "send_email":
            score = kwargs.get("score", 0)
            match_analysis = kwargs.get("match_analysis", "")
            return email_agent.generate_email(
                kwargs["cv_summary"], 
                kwargs["job_summary"], 
                score,
                match_analysis
            )
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    except Exception as e:
        return f"Error in task '{task_type}': {str(e)}"
