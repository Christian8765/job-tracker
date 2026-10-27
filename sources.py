import html
import re
import requests

def clean_description(html_text):
    text = html.unescape(html_text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def fetch_greenhouse(company, slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    results = []
    for job in response.json()["jobs"]:
        results.append({
            "company": company,
            "job_id": str(job["id"]),
            "title": job["title"],
            "location": job["location"]["name"],
            "url": job["absolute_url"],
            "description": clean_description(job.get("content", ""))
        })

    return results