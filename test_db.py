from db import connect, save_and_get_new


def make_job(job_id):
    return {"company": "TestCo", "job_id": job_id, "title": "Backend Engineer",
            "location": "New York", "url": "https://example.com", "description": ""}


def run_tests():
    conn = connect(":memory:")

    first = save_and_get_new(conn, [make_job("1"), make_job("2")])
    assert len(first) == 2          # both new

    second = save_and_get_new(conn, [make_job("1"), make_job("2")])
    assert len(second) == 0         # nothing new

    third = save_and_get_new(conn, [make_job("2"), make_job("3")])
    assert len(third) == 1          # only 3 is new
    assert third[0]["job_id"] == "3"


if __name__ == "__main__":
    run_tests()
    print("All db tests passed")