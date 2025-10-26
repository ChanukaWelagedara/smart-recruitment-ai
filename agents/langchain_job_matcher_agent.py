import re
from abc import ABC
from config.langchain_config import LangChainConfig

try:
    from langchain_community.tools import DuckDuckGoSearchRun
except ImportError:
    DuckDuckGoSearchRun = None

from agents.base_agent import BaseAgent

class LangChainJobMatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__("job_matcher_agent")
        self.llm = LangChainConfig.get_llm()

        try:
            if DuckDuckGoSearchRun:
                self.search_tool = DuckDuckGoSearchRun()
            else:
                self.search_tool = None
        except Exception as e:
            print(f"Warning: Could not initialize search tool: {e}")
            self.search_tool = None

    def can_handle(self, task_type: str) -> bool:
        return task_type == "match_cv"

    def perform_task(self, data: dict, context: dict = None):
        cv_summary = data.get("cv_summary", "")
        job_summary = data.get("job_summary", "")
        github_summary = data.get("github_summary", "") 
        if not cv_summary or not job_summary or not github_summary:
            return {"error": "Missing cv_summary or job_summary or github_summary"}

        return self.match_cv_to_job(cv_summary, job_summary, github_summary)

    def match_cv_to_job(self, cv_summary: str, job_summary: str, github_summary: str):
        try:
            market_info = ""
            try:
                if self.search_tool:
                    market_query = "current job market trends hiring requirements software development 2024"
                    market_info = self.search_tool.run(market_query)
                else:
                    market_info = "Market research unavailable - search tool not available"
            except Exception as e:
                market_info = f"Market research unavailable: {str(e)}"

            prompt = f"""
Analyze the compatibility between this candidate and job position:

CANDIDATE PROFILE:
{cv_summary}
GiTHUB PROFILE:
GitHub Summary (projects, code quality, contributions, skills):
{github_summary if github_summary else "GitHub data not available"}

JOB REQUIREMENTS:
{job_summary}

CURRENT MARKET INSIGHTS:
{market_info}

Please provide a comprehensive matching analysis:

1. OVERALL MATCH SCORE: [0-100%]

2. SKILL ALIGNMENT:
   - Perfectly Matching Skills: [list]
   - Partially Matching Skills: [list]
   - Missing Critical Skills: [list]
   - Additional Skills (bonus): [list]

3. EXPERIENCE ANALYSIS:
   - Years of Experience Match: [Excellent/Good/Fair/Poor]
   - Industry Experience: [Relevant/Somewhat Relevant/Not Relevant]
   - Role Level Match: [Overqualified/Perfect Fit/Underqualified]

4. TECHNICAL ASSESSMENT:
   - Programming Languages: [match percentage]
   - Frameworks/Technologies: [match percentage]
   - Tools and Platforms: [match percentage]

5. HIRING RECOMMENDATION:
   - Decision: [Strong Hire/Hire/Maybe/No Hire]
   - Confidence Level: [High/Medium/Low]
   - Reasons for recommendation

6. INTERVIEW FOCUS AREAS:
   - Key areas to explore in interview
   - Potential concerns to address
   - Questions to ask candidate

Provide detailed analysis:
"""

            if hasattr(self.llm, 'invoke'):
                from langchain_core.messages import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content
            elif hasattr(self.llm, 'chat'):
                response = self.llm.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    temperature=0.1,
                    max_tokens=2048
                )
                return response.choices[0].message.content
            else:
                return "Job matching analysis for candidate based on CV and job requirements."

        except Exception as e:
            return f"Error matching CV to job: {str(e)}"


def extract_match_score(analysis_text: str) -> int:
    try:
        match = re.search(r'OVERALL MATCH SCORE:\s*(\d{1,3})%', analysis_text, re.IGNORECASE)
        if match:
            score = int(match.group(1))
            print(f"[DEBUG] Extracted score: {score}")
            return score
    except Exception as e:
        print(f"[DEBUG] Error extracting score: {e}")
    return 0
