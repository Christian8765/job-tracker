from filters import title_matches, location_matches, too_much_experience, is_clearance
from sources import fetch_greenhouse

def main():
    jobs = fetch_greenhouse("Anthropic", "anthropic")

    match_count = 0
    for job in jobs:
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

    print(f"\n{match_count} matches out of {len(jobs)} jobs")


if __name__ == "__main__":
    main()