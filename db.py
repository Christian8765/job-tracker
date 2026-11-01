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
);

CREATE TABLE IF NOT EXISTS board_runs (
    company TEXT NOT NULL,
    job_count INTEGER NOT NULL,
    run_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_JOB = """
INSERT INTO jobs (company, job_id, title, location, url)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT (company, job_id) DO NOTHING
"""

INSERT_RUN = "INSERT INTO board_runs (company, job_count) VALUES (?, ?)"

LAST_THREE_RUNS = """
SELECT job_count FROM board_runs
WHERE company = ?
ORDER BY rowid DESC
LIMIT 3
"""


def connect(path="jobs.db"):
    conn = sqlite3.connect(path)
    conn.executescript(SCHEMA)
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

def record_board_run(conn, company, count):
    conn.execute(INSERT_RUN, (company, count))
    conn.commit()


def broken_boards(conn, companies):
    broken = []
    for company in companies:
        rows = conn.execute(LAST_THREE_RUNS, (company,)).fetchall()
        if len(rows) == 3 and all(row[0] == 0 for row in rows):
            broken.append(company)
    return broken