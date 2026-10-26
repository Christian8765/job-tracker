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

WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

EXPERIENCE_PATTERN = r"(\d+)\s*\+?\s*(?:or more\s+)?years?"

CLEARANCE_TERMS = ["clearance", "secret", "ts/sci"]

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

run_tests()

firstJobContent = jobs[0].get("content", "")
cleaned = clean_description(firstJobContent)
print("\n--- Cleaned Description Preview (First 300 chars) ---")
print(cleaned[:300])

