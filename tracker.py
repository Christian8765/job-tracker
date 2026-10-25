import requests

URL = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"

response = requests.get(URL, timeout=15)
print(response.status_code)

data = response.json()
jobs = data["jobs"]
print(len(jobs))

# task 4
for job in jobs:
    print(job["title"])