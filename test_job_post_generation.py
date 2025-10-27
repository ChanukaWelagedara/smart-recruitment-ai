from agents.job_post_generation_agent import JobPostGenerationAgent


def test_agent_direct():
    agent = JobPostGenerationAgent()
    payload = {
        "job_title": "Cpmputer Scientist",
        "qualifications": "Bachelor's in Computer Science or related field, experience with Python and Flask",
        "salary": "$70,000 - $90,000 per year",
        "responsibilities": "Develop REST APIs, integrate AI modules, maintain backend architecture"
    }

    result = agent.perform_task(payload)
    assert isinstance(result, dict)
    assert result.get("status") == "success"
    assert "formatted_job_post" in result
    assert "Job Title: Software Engineer" in result["formatted_job_post"]

