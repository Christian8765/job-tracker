from db import connect, save_and_get_new, record_board_run, broken_boards


def make_job(job_id):
    return {"company": "TestCo", "job_id": job_id, "title": "Backend Engineer",
            "location": "New York", "url": "https://example.com", "description": ""}


def test_save_and_get_new():
    conn = connect(":memory:")

    first = save_and_get_new(conn, [make_job("1"), make_job("2")])
    assert len(first) == 2

    second = save_and_get_new(conn, [make_job("1"), make_job("2")])
    assert len(second) == 0

    third = save_and_get_new(conn, [make_job("2"), make_job("3")])
    assert len(third) == 1
    assert third[0]["job_id"] == "3"


def test_broken_boards():
    conn = connect(":memory:")
    for _ in range(3):
        record_board_run(conn, "DeadCo", 0)
        record_board_run(conn, "LiveCo", 50)
    record_board_run(conn, "NewCo", 0)

    assert broken_boards(conn, ["DeadCo", "LiveCo", "NewCo"]) == ["DeadCo"]