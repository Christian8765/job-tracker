import requests
import re
import html

URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"

response = requests.get(URL, timeout=15)
print(response.status_code)

data = response.json()
jobs = data["jobs"]
print(len(jobs))

# task 4
# for job in jobs:
#     print(job["title"])

# task 5
INCLUDE = ["software engineer", "backend", "back-end", "platform engineer", "infrastructure engineer",
           "developer", "api", "data engineer"]
EXCLUDE = ["senior", "sr", "staff", "principal", "lead", "manager", "director", "head of",
           "architect", "iii", "iv"]

LOCATIONS = ["nyc", "new york city", "new york", "remote"]

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

run_tests()

firstJobContent = jobs[0].get("content", "")
cleaned = clean_description(firstJobContent)
print("\n--- Cleaned Description Preview (First 300 chars) ---")
print(cleaned[:300])