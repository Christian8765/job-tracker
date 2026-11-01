import csv
import time
import argparse
import requests
import logging

from filters import title_matches, location_matches, too_much_experience, is_clearance
from sources import fetch_greenhouse, fetch_ashby, fetch_workday, fetch_eightfold, fetch_details 
from db import connect, save_and_get_new, record_board_run, broken_boards
from datetime import date

def print_job(job):
    tag = "[CLEARANCE]" if is_clearance(job["description"]) else ""
    print(f"{job['company']} | {job['title']} | {job['location']} | {tag} | {job['url']}")

def md_escape(text):
    return text.replace("|", "\\|")

def write_report(path, new_jobs, matches, broken):
    lines = [f"# Job check: {date.today()}", ""]

    if broken:
        logging.warning(f"Boards with 0 jobs 3 runs in a row: {', '.join(broken)}")
        lines.append("## ⚠️ Boards needing attention")
        lines.append("")
        for company in broken:
            lines.append(f"- {company}: 0 jobs for 3 runs in a row")
        lines.append("")

    lines.append(f"## New today ({len(new_jobs)})")
    lines.append("")
    if new_jobs:
        lines.append("| Company | Title | Location | Clearance | Link |")
        lines.append("|---|---|---|---|---|")
        for job in new_jobs:
            clearance = "Yes" if is_clearance(job["description"]) else ""
            lines.append(
                f"| {md_escape(job['company'])} | {md_escape(job['title'])} | "
                f"{md_escape(job['location'])} | {clearance} | [Apply]({job['url']}) |"
            )

    else:
        lines.append("No new jobs today.")

    lines.append("")
    lines.append(f"## All current matches ({len(matches)})")
    lines.append("")
    for job in matches:
        lines.append(f"- {md_escape(job['company'])}: [{md_escape(job['title'])}]({job['url']})")

    with open(path, "w") as f:
        f.write("\n".join(lines) + "\n")


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="Find new backend-adjacent jobs.")
    parser.add_argument("--all", action="store_true", help="show all current matches, not just new ones")
    parser.add_argument("--db", default="local.db", help="database file to use")
    parser.add_argument("--report", help="also write results to this markdown file")
    args = parser.parse_args()

    with open("boards.csv") as f:
        boards = list(csv.DictReader(f))

    # 1. Gather: fetch jobs from every board
    all_jobs = []
    failures = []
    conn = connect(args.db)
    for row in boards:
        try:
            if row["ats"] == "greenhouse":
                jobs = fetch_greenhouse(row["company"], row["slug"])
            elif row["ats"] == "ashby":
                jobs = fetch_ashby(row["company"], row["slug"])
            elif row["ats"] == "workday":
                jobs = fetch_workday(row["company"], row["slug"])
            elif row["ats"] == "eightfold":
                jobs = fetch_eightfold(row["company"], row["slug"])
            else:
                logging.warning(f"Skipping {row['company']}: unknown ATS {row['ats']}")
                continue
        except requests.RequestException as e:
            logging.error(f"FAILED {row['company']}: {e}")
            failures.append(row["company"])
            record_board_run(conn, row["company"], 0)
            continue

        record_board_run(conn, row["company"], len(jobs))
        all_jobs.extend(jobs)
        logging.info(f"{row['company']}: {len(jobs)} jobs fetched")
        time.sleep(1)

    # 2. Filter: keep only jobs that match
    matches = []
    for job in all_jobs:
        if not title_matches(job["title"]):
            continue

        if job["description"] is None:
            try:
                job.update(fetch_details(job))
            except requests.RequestException as e:
                logging.warning(f"Could not load details for {job['company']} | {job['title']}: {e}")
                continue
            time.sleep(0.5)

        if not location_matches(job["location"]):
            continue
        if too_much_experience(job["description"]):
            continue
        matches.append(job)

    # 3. Save: store matches, find which are new
    new_jobs = save_and_get_new(conn, matches)
    broken = broken_boards(conn, [row["company"] for row in boards])
    conn.close()

    # 4. Report
    to_show = matches if args.all else new_jobs
    for job in to_show:
        print_job(job)
    print(f"\n{len(new_jobs)} new out of {len(matches)} matches ({len(all_jobs)} jobs checked)")

    if failures:
        print(f"Failed boards: {', '.join(failures)}")

    if args.report:
        write_report(args.report, new_jobs, matches, broken)
        print(f"Report written to {args.report}")


if __name__ == "__main__":
    main()