"""OSS-Fuzz-Research"""

import httpx
from dotenv import load_dotenv

load_dotenv()


PROJECTS_ENDPOINT = "https://api.github.com/repos/google/oss-fuzz/contents/projects"


def get_projects():
    response = httpx.get(PROJECTS_ENDPOINT)
    projects = [
        {
            "name": project["name"],
            "url": project["html_url"],
        }
        for project in response.json()
    ]
    return projects
