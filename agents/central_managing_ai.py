from .langchain_cv_summary_agent import LangChainCVSummaryAgent
from .langchain_job_matcher_agent import LangChainJobMatcherAgent
from .langchain_interview_agent import LangChainInterviewAgent
from .langchain_email_generation_agent import LangChainEmailGenerationAgent
from .langchain_cv_info_extractor_agent import LangChainCVInfoExtractorAgent
from .file_download_agent import FileDownloadAgent
from .data_privacy_agent import DataPrivacyAgent
from .job_post_generation_agent import JobPostGenerationAgent
from .task_manager import TaskManager
from. langchain_github_summary_agent import LangChainGitHubSummaryAgent

existing_agents = [
    LangChainCVSummaryAgent(),
    LangChainJobMatcherAgent(),
    LangChainInterviewAgent(),
    LangChainEmailGenerationAgent(),
    LangChainCVInfoExtractorAgent(),
    JobPostGenerationAgent(),
    LangChainGitHubSummaryAgent(),
]


infra_agents = [
    FileDownloadAgent(),
    DataPrivacyAgent()
]

# All agents combined
all_agents = existing_agents + infra_agents

# Create TaskManager instance
task_manager = TaskManager(all_agents)

def run_task(task_type: str, **kwargs):

    return task_manager.run_task(task_type, kwargs)

def run_full_application_pipeline(job_post: dict, candidates: list):
 
    return task_manager.orchestrate_application(job_post, candidates)
