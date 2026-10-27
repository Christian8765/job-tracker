import requests
import re
import html
from filters import title_matches, location_matches, is_clearance, too_much_experience
from sources import clean_description

URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"

def main():
    response = requests.get(URL, timeout=15)
    response.raise_for_status()
    jobs = response.json()["jobs"]

    match_count = 0
    for job in jobs:
        title = job["title"]
        location = job["location"]["name"]
        url = job["absolute_url"]

        if not title_matches(title):
            continue
        if not location_matches(location):
            continue

        description = clean_description(job.get("content", ""))
        if too_much_experience(description):
            continue

        tag = "[CLEARANCE]" if is_clearance(description) else ""
        print(f"{title} | {location} | {tag} | {url}")
        match_count += 1

    print(f"\n{match_count} matches out of {len(jobs)} jobs")

if __name__ == "__main__":
    main()