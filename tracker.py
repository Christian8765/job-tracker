import csv
import time

import requests

from filters import title_matches, location_matches, too_much_experience, is_clearance
from sources import fetch_greenhouse, fetch_ashby


def main():
    with open("boards.csv") as f:
        boards = list(csv.DictReader(f))

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

    if failures:
        print(f"Failed boards: {', '.join(failures)}")


if __name__ == "__main__":
    main()