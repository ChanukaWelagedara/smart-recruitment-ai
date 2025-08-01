# utils/file_utils.py
import requests
import os

def download_pdf_from_url(url, save_dir="data/cv_pdfs", filename=None):
    try:
        os.makedirs(save_dir, exist_ok=True)
        if not filename:
            filename = url.split("/")[-1]
        file_path = os.path.join(save_dir, filename)
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            return file_path
        else:
            print(f"❌ Failed to download file: {url} (status code {response.status_code})")
            return None
    except Exception as e:
        print(f"❌ Error downloading PDF from URL: {e}")
        return None
