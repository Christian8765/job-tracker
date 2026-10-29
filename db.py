import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    company TEXT NOT NULL,
    job_id TEXT NOT NULL,
    title TEXT,
    location TEXT,
    url TEXT,
    first_seen TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (company, job_id)
)
"""

INSERT_JOB = """
INSERT INTO jobs (company, job_id, title, location, url)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT (company, job_id) DO NOTHING
"""


def connect(path="jobs.db"):
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def save_and_get_new(conn, jobs):
    new_jobs = []
    for job in jobs:
        cur = conn.execute(
            INSERT_JOB,
            (job["company"], job["job_id"], job["title"], job["location"], job["url"]),
        )
        if cur.rowcount == 1:
            new_jobs.append(job)
    conn.commit()
    return new_jobs