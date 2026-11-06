import html
import re
import requests
import time
import logging
from urllib.parse import urlparse, parse_qs

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
            if "title" not in job or "externalPath" not in job:
                logging.warning(f"(company): skipping incomplete posting: {job}")
                continue
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

def parse_greenhouse(company, data):
    results = []
    for job in data["jobs"]:
        results.append({
            "company": company,
            "job_id": str(job["id"]),
            "title": job["title"],
            "location": job["location"]["name"],
            "url": job["absolute_url"],
            "description": clean_description(job.get("content", "")),
        })
    return results


def fetch_greenhouse(company, slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return parse_greenhouse(company, response.json())

def parse_ashby(company, data):
    results = []
    for job in data["jobs"]:
        locations = [job["location"]]
        for extra in job.get("secondaryLocations", []):
            locations.append(extra["location"])
        if job.get("workplaceType") == "Remote":
            locations.append("Remote")

        description = job.get("descriptionPlain") or clean_description(job.get("descriptionHtml", ""))

        results.append({
            "company": company,
            "job_id": str(job["id"]),
            "title": job["title"].strip(),
            "location": " | ".join(locations),
            "url": job["jobUrl"],
            "description": description,
        })
    return results


def fetch_ashby(company, slug):
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}"
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return parse_ashby(company, response.json())

def fetch_eightfold(company, search_url):
    parts = urlparse(search_url)
    host = parts.netloc
    base = f"https://{host}{parts.path}"
    params = {k: v[0] for k, v in parse_qs(parts.query, keep_blank_values=True).items()}
    domain = params["domain"]

    results = []
    start = 0
    total = None
    while True:
        params["start"] = start
        r = requests.get(base, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()["data"]

        if total is None:
            total = data.get("count", 0)
        positions = data.get("positions", [])
        if not positions:
            break

        for job in positions:
            locations = list(job.get("locations", []))
            if "remote" in job.get("workLocationOption", ""):
                locations.append("Remote")
            results.append({
                "company": company,
                "job_id": str(job["id"]),
                "title": job["name"].strip(),
                "location": " | ".join(locations),
                "url": f"https://{host}{job['positionUrl']}",
                "description": None,
                "detail_url": f"https://{host}/api/pcsx/position_details?position_id={job['id']}&domain={domain}",
            })

        start += len(positions)
        if start >= total:
            break
        time.sleep(0.5)

    return results

def fetch_eightfold_details(detail_url):
    r = requests.get(detail_url, timeout=15)
    r.raise_for_status()
    info = r.json()["data"]
    return {"description": clean_description(info.get("jobDescription", ""))}


def fetch_details(job):
    if "myworkdayjobs.com" in job["detail_url"]:
        return fetch_workday_details(job["detail_url"])
    return fetch_eightfold_details(job["detail_url"])