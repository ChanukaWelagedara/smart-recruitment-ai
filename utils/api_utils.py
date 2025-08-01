import requests

def fetch_candidate_data(api_url: str):
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            return data["data"]
        else:
            raise ValueError("API returned failure status")
    except Exception as e:
        print(f"❌ Failed to fetch candidate data: {e}")
        return None
