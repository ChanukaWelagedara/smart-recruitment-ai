import requests

def scrape_github_profile(username: str) -> dict:
    """Fetch GitHub profile and top 10 repositories using the GitHub API."""
    try:
        # Fetch user profile
        profile_res = requests.get(f"https://api.github.com/users/{username}", timeout=10)
        if profile_res.status_code != 200:
            return {"error": f"Failed to fetch profile: {profile_res.status_code}"}
        profile = profile_res.json()

        # Fetch user's top 10 most recently updated repos
        repos_res = requests.get(
            f"https://api.github.com/users/{username}/repos?sort=updated&per_page=10",
            timeout=10
        )
        if repos_res.status_code != 200:
            return {"error": f"Failed to fetch repos: {repos_res.status_code}"}
        repos = repos_res.json()

        simplified_repos = []
        for r in repos:
            simplified_repos.append({
                "name": r.get("name"),
                "description": r.get("description"),
                "language": r.get("language"),
                "stars": r.get("stargazers_count"),
                "fork": r.get("fork"),
                "updated_at": r.get("updated_at")
            })

        return {
            "profile": {
                "name": profile.get("name"),
                "bio": profile.get("bio"),
                "location": profile.get("location"),
                "public_repos": profile.get("public_repos"),
                "followers": profile.get("followers")
            },
            "repositories": simplified_repos
        }

    except Exception as e:
        return {"error": f"Exception while fetching GitHub data: {str(e)}"}
