import re

URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"

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

def is_clearance(text):
    t = text.lower()
    return any(re.search(rf"\b{word}\b", t) for word in CLEARANCE_TERMS)