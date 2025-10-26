from agents.base_agent import BaseAgent


class JobPostGenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__("job_post_generation_agent")

    def can_handle(self, task_type: str) -> bool:
        return task_type == "generate_job_post"

    def perform_task(self, data: dict, context: dict = None):
        try:
            # Accept multiple possible key namings to be resilient
            job_title = data.get("job_title") or data.get("jobTitle") or data.get("title") or ""
            qualifications = data.get("qualifications") or data.get("qualification") or ""
            salary = data.get("salary") or data.get("pay") or ""
            responsibilities = data.get("responsibilities") or data.get("responsibility") or ""

            def to_bullets(text: str):
                if not text:
                    return []
                # Normalize common separators into list items
                # Prefer existing newlines, otherwise split on commas or semicolons
                if "\n" in text:
                    parts = [line.strip() for line in text.splitlines() if line.strip()]
                elif "," in text:
                    parts = [p.strip() for p in text.split(",") if p.strip()]
                elif ";" in text:
                    parts = [p.strip() for p in text.split(";") if p.strip()]
                else:
                    parts = [text.strip()]
                return parts

            qual_list = to_bullets(qualifications)
            resp_list = to_bullets(responsibilities)

            lines = []
            # Header
            lines.append(f"Job Title: {job_title}")
            lines.append("")

            # Salary
            if salary:
                lines.append(f"Salary: {salary}")
                lines.append("")

            # Qualifications
            lines.append("Qualifications:")
            if qual_list:
                for q in qual_list:
                    lines.append(f"• {q}")
            else:
                lines.append("• Not specified")

            lines.append("")

            # Responsibilities
            lines.append("Responsibilities:")
            if resp_list:
                for r in resp_list:
                    lines.append(f"• {r}")
            else:
                lines.append("• Not specified")

            formatted = "\n".join(lines)

            return {"status": "success", "formatted_job_post": formatted}

        except Exception as e:
            return {"status": "error", "error": str(e)}
