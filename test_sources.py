import json

from sources import parse_workday_url, parse_greenhouse, parse_ashby

SIX_KEYS = {"company", "job_id", "title", "location", "url", "description"}


def load(path):
    with open(path) as f:
        return json.load(f)


def test_parse_workday_url():
    assert parse_workday_url("https://visa.wd5.myworkdayjobs.com/Visa") == (
        "visa.wd5.myworkdayjobs.com", "visa", "Visa")
    assert parse_workday_url("https://livenation.wd503.myworkdayjobs.com/en-US/TMExternalSite") == (
        "livenation.wd503.myworkdayjobs.com", "livenation", "TMExternalSite")


def test_parse_greenhouse():
    data = load("tests/fixtures/greenhouse.json")
    jobs = parse_greenhouse("Anthropic", data)

    assert len(jobs) == len(data["jobs"])
    assert jobs[0]["company"] == "Anthropic"
    assert jobs[0]["title"] == data["jobs"][0]["title"]
    assert set(jobs[0].keys()) == SIX_KEYS
    assert "<" not in jobs[0]["description"]


def test_parse_ashby():
    data = load("tests/fixtures/ashby.json")
    jobs = parse_ashby("Strava", data)

    assert len(jobs) == len(data["jobs"])
    assert jobs[0]["company"] == "Strava"
    assert jobs[0]["title"] == data["jobs"][0]["title"].strip()
    assert set(jobs[0].keys()) == SIX_KEYS
    assert "<" not in jobs[0]["description"]