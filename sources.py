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

def fetch_ashby(company, slug): 
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    results = []
    for job in response.json()["jobs"]:
        locations = [job["location"]]
        for extra in job.get("secondaryLocations", []):
            locations.append(extra["location"])

        if job.get("workplaceType") == "Remote":
            locations.append("Remote")
        location = " | ".join(locations)

        description = job.get("descriptionPlain") or clean_description(job.get("" \
        "descriptionHtml", ""))

        results.append({
            "company": company,
            "job_id": str(job["id"]),
            "title": job["title"].strip(),
            "location": location,
            "url": job["jobUrl"],
            "description": description
        })

    return results