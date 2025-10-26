# agents/langchain_github_summary_agent.py
from agents.base_agent import BaseAgent
from config.langchain_config import LangChainConfig
from utils.github_scraper import scrape_github_profile
from urllib.parse import urlparse

class LangChainGitHubSummaryAgent(BaseAgent):
    def __init__(self):
        super().__init__("github_summary_agent")
        self.llm = LangChainConfig.get_llm()

    def extract_username(self, github_url: str) -> str:
        """Extract GitHub username from full URL."""
        parsed = urlparse(github_url)
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) >= 1:
            return path_parts[0]
        return github_url 
    
    def can_handle(self, task_type: str) -> bool:
        return task_type in ["summarize_github", "summarize_github_profile"]

    def perform_task(self, data: dict, context: dict = None):
        github_url = data.get("github_url")
        if not github_url:
            return "Error: 'github_url' is required"
        username = self.extract_username(github_url)
        try:
            github_data = scrape_github_profile(username)
        except Exception as e:
            return f"Error scraping GitHub: {str(e)}"

        prompt = f"""
Analyze this GitHub profile and summarize the candidate's technical strengths and coding style.

GitHub Profile Data:
{github_data}

Please provide:
1. Overview of coding activity
2. Key programming languages and frameworks
3. Notable projects or repositories
4. Code quality and documentation
5. Strengths and possible improvement areas
"""

        try:
            if hasattr(self.llm, "invoke"):
                from langchain_core.messages import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content
            elif hasattr(self.llm, "chat"):
                response = self.llm.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    max_tokens=2048
                )
                return response.choices[0].message.content
            else:
                return f"GitHub Summary for {github_url}:\n\n{github_data[:500]}..."

        except Exception as e:
            return f"Error generating GitHub summary: {str(e)}"
