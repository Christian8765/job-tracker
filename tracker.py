import csv
import time
import argparse
import requests

from filters import title_matches, location_matches, too_much_experience, is_clearance
from sources import fetch_greenhouse, fetch_ashby
from db import connect, save_and_get_new

def print_job(job):
    tag = "[CLEARANCE]" if is_clearance(job["description"]) else ""
    print(f"{job['company']} | {job['title']} | {job['location']} | {tag} | {job['url']}")

def main():
    parser = argparse.ArgumentParser(description="Find new backend-adjacent jobs.")
    parser.add_argument("--all", action="store_true", help="show all current matches, not just new ones")
    args = parser.parse_args()

    with open("boards.csv") as f:
        boards = list(csv.DictReader(f))

    # 1. Gather: fetch jobs from every board
    all_jobs = []
    failures = []
    for row in boards:
        try:
            if row["ats"] == "greenhouse":
                jobs = fetch_greenhouse(row["company"], row["slug"])
            elif row["ats"] == "ashby":
                jobs = fetch_ashby(row["company"], row["slug"])
            else:
                print(f"Skipping {row['company']}: unknown ATS {row['ats']}")
                continue
        except requests.RequestException as e:
            print(f"FAILED {row['company']}: {e}")
            failures.append(row["company"])
            continue

        all_jobs.extend(jobs)
        time.sleep(1)

    # 2. Filter: keep only jobs that match
    matches = []
    for job in all_jobs:
        if not title_matches(job["title"]):
            continue
        if not location_matches(job["location"]):
            continue
        if too_much_experience(job["description"]):
            continue
        matches.append(job)

    # 3. Save: store matches, find which are new
    conn = connect()
    new_jobs = save_and_get_new(conn, matches)
    conn.close()

    # 4. Report
    # 4. Report
    to_show = matches if args.all else new_jobs
    for job in to_show:
        print_job(job)
    print(f"\n{len(new_jobs)} new out of {len(matches)} matches ({len(all_jobs)} jobs checked)")

    if failures:
        print(f"Failed boards: {', '.join(failures)}")


if __name__ == "__main__":
    main()