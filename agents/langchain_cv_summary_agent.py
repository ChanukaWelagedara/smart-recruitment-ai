import os
import glob
#from agents.central_managing_ai import run_task  # Uncomment and import your run_task function
from utils.pdf_utils import extract_text_from_pdf
from database.langchain_vector_db import LangChainVectorDB
from utils.linkedin_scraper import scrape_linkedin
from config.langchain_config import LangChainConfig
from langchain_community.document_loaders import PyPDFLoader
from langchain.prompts import PromptTemplate


class LangChainCVSummaryAgent:
    def __init__(self):
        self.llm = LangChainConfig.get_llm()
    
    def summarize_cv(self, cv_path: str, linkedin_url: str = None):
        """Summarize CV using either LangChain ChatGroq or direct Groq API"""
        try:
            # Extract CV text using existing utility
            cv_text = extract_text_from_pdf(cv_path)
            
            if not cv_text:
                return "Error: Could not extract text from CV"
            
            # Get LinkedIn data if URL provided
            linkedin_data = ""
            if linkedin_url:
                try:
                    linkedin_data = scrape_linkedin(linkedin_url)
                except Exception as e:
                    linkedin_data = f"LinkedIn scraping failed: {str(e)}"
            else:
                linkedin_data = "No LinkedIn URL provided"
            
            # Create comprehensive prompt
            prompt = f"""
            Analyze this candidate's CV and create a comprehensive summary:
            
            CV CONTENT:
            {cv_text[:4000]}  # Limit text to avoid token limits
            
            LINKEDIN DATA:
            {linkedin_data}
            
            Please provide a detailed candidate summary including:
            
            1. PERSONAL INFORMATION:
               - Full Name and Contact Information
               - Professional Title
            
            2. PROFESSIONAL SUMMARY:
               - Years of experience
               - Industry expertise
               - Key specializations
            
            3. TECHNICAL SKILLS:
               - Programming Languages
               - Frameworks and Technologies
               - Tools and Platforms
            
            4. WORK EXPERIENCE:
               - Current/Recent Position
               - Key achievements
               - Notable projects
            
            5. EDUCATION:
               - Degrees and institutions
               - Relevant certifications
            
            6. STRENGTHS:
               - Technical strengths
               - Soft skills
               - Growth potential
            
            Provide a comprehensive, professional summary:
            """
            
            # Check if we have LangChain ChatGroq or direct Groq client
            if hasattr(self.llm, 'invoke'):
                # LangChain ChatGroq - use correct format
                from langchain_core.messages import HumanMessage
                response = self.llm.invoke([HumanMessage(content=prompt)])
                return response.content
            elif hasattr(self.llm, 'chat'):
                # Direct Groq client
                response = self.llm.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",  # Updated to current model
                    temperature=0.1,
                    max_tokens=2048
                )
                return response.choices[0].message.content
            else:
                # Fallback - try to use as string input
                return f"CV Summary for {cv_path}: {cv_text[:500]}..."
            
        except Exception as e:
            return f"Error summarizing CV: {str(e)}"
        

