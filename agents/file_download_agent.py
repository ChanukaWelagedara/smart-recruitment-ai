from agents.base_agent import BaseAgent
from utils.file_utils import download_pdf_from_url
import os

class FileDownloadAgent(BaseAgent):
    def __init__(self):
        super().__init__("file_download_agent")

    def can_handle(self, task_type: str) -> bool:
        return task_type == "download_file"

    def perform_task(self, data: dict, context: dict = None):
        url = data.get("url")
        filename = data.get("filename")
        save_dir = data.get("save_dir", "data/cv_pdfs")
        if not url or not filename:
            return {"error": "Missing 'url' or 'filename'"}

        os.makedirs(save_dir, exist_ok=True)
        file_path = download_pdf_from_url(url, save_dir, filename)
        if not file_path:
            return {"error": "Download failed"}
        return {"file_path": file_path}
