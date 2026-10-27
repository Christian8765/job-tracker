import csv

from filters import title_matches, location_matches, too_much_experience, is_clearance
from sources import fetch_greenhouse


def main():
    with open("boards.csv") as f:
        boards = list(csv.DictReader(f))

    all_jobs = []
    for row in boards:
        if row["ats"] != "greenhouse":
            continue
        jobs = fetch_greenhouse(row["company"], row["slug"])
        all_jobs.extend(jobs)

    match_count = 0
    for job in all_jobs:
        company = job["company"]
        title = job["title"]
        location = job["location"]
        url = job["url"]
        description = job["description"]

        if not title_matches(title):
            continue
        if not location_matches(location):
            continue
        if too_much_experience(description):
            continue

        tag = "[CLEARANCE]" if is_clearance(description) else ""
        print(f"{company} | {title} | {location} | {tag} | {url}")
        match_count += 1

    print(f"\n{match_count} matches out of {len(all_jobs)} jobs")


if __name__ == "__main__":
    main()