import html
import re
import requests
import time
from urllib.parse import urlparse

def parse_workday_url(careers_url):
    parsed = urlparse(careers_url)
    host = parsed.netloc
    tenant = host.split(".")[0]
    site = parsed.path.strip("/").split("/")[-1]
    return host, tenant, site

def fetch_workday(company, careers_url):
    host, tenant, site = parse_workday_url(careers_url)
    api = f"https://{host}/wday/cxs/{tenant}/{site}"

    results = []
    offset = 0
    total = None
    while True:
        body = {"appliedFacets": {}, "limit": 20, "offset": offset, "searchText": ""}
        r = requests.post(f"{api}/jobs", json=body,
                          headers={"Accept": "application/json"}, timeout=15)
        r.raise_for_status()
        data = r.json()

        if total is None:
            total = data.get("total", 0)
        postings = data.get("jobPostings", [])
        if not postings:
            break

        for job in postings:
            path = job["externalPath"]
            results.append({
                "company": company,
                "job_id": path,
                "title": job["title"].strip(),
                "location": job.get("locationsText", ""),
                "url": f"https://{host}/{site}{path}",
                "description": None,
                "detail_url": f"{api}{path}",
            })

        offset += len(postings)
        if offset >= total:
            break
        time.sleep(0.5)

    return results

def fetch_workday_details(detail_url):
    r = requests.get(detail_url, headers={"Accept": "application/json"}, timeout=15)
    r.raise_for_status()
    info = r.json()["jobPostingInfo"]

    locations = [info.get("location", "")] + info.get("additionalLocations", [])
    return {
        "location": " | ".join(loc for loc in locations if loc), 
        "description": clean_description(info.get("jobDescription", ""))
    }


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

