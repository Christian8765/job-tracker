import requests
import re
import html

URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"

# task 5
INCLUDE = ["software engineer", "backend", "back-end", "platform engineer", "infrastructure engineer",
           "developer", "api", "data engineer"]
EXCLUDE = ["senior", "sr", "staff", "principal", "lead", "manager", "director", "head of",
           "architect", "iii", "iv"]

LOCATIONS = ["nyc", "new york city", "new york", "remote"]

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

CLEARANCE_TERMS = ["clearance", "secret", "ts/sci"]

EXPERIENCE_PATTERN = r"(\d+)\s*\+?\s*(?:or more\s+)?years?"

def too_much_experience(text):
    text = text.lower()
    for word, number in WORD_NUMBERS.items():
        text = re.sub(rf"\b{word}\b", str(number), text)
    matches = re.findall(EXPERIENCE_PATTERN, text)
    for m in matches: 
        if int(m) >= 5:
            return True
    return False

def title_matches(title):
    t = title.lower()
    if any(re.search(rf"\b{word}\b", t) for word in EXCLUDE):
        return False
    if any(re.search(rf"\b{word}\b", t) for word in INCLUDE):
        return True
    return False

def location_matches(location):
    t = location.lower()
    if any(re.search(rf"\b{word}\b", t) for word in LOCATIONS):
        return True
    return False

def clean_description(html_text):
    text = html.unescape(html_text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def is_clearance(text):
    t = text.lower()
    return any(re.search(rf"\b{word}\b", t) for word in CLEARANCE_TERMS)
    
def run_tests():
    assert title_matches("Software Engineer, Backend") == True
    assert title_matches("Data Engineer") == True
    assert title_matches("Senior Software Engineer") == False
    assert title_matches("Engineering Manager") == False
    assert title_matches("Account Executive") == False
    assert title_matches("Staff Infrastructure Engineer") == False
    assert title_matches("Capital Markets Analyst") == False
    assert location_matches("New York City, NY") == True
    assert location_matches("Remote-Friendly, United States") == True
    assert location_matches("San Francisco, CA | New York City, NY") == True
    assert location_matches("London, UK") == False
    assert too_much_experience("5+ years of experience") == True
    assert too_much_experience("minimum of 7 years") == True
    assert too_much_experience("10 years of experience") == True
    assert too_much_experience("five years of experience") == True
    assert too_much_experience("5 or more years") == True
    assert too_much_experience("3+ years of experience") == False
    assert too_much_experience("2-4 years of experience") == False
    assert too_much_experience("no experience required") == False
    assert is_clearance("Active Secret clearance required") == True
    assert is_clearance("Executive Secretary") == False
    assert is_clearance("Python and AWS") == False

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
    run_tests()
    main()