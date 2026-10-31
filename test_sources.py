from sources import parse_workday_url


def run_tests():
    assert parse_workday_url("https://visa.wd5.myworkdayjobs.com/Visa") == (
        "visa.wd5.myworkdayjobs.com", "visa", "Visa")
    assert parse_workday_url("https://livenation.wd503.myworkdayjobs.com/en-US/TMExternalSite") == (
        "livenation.wd503.myworkdayjobs.com", "livenation", "TMExternalSite")


if __name__ == "__main__":
    run_tests()
    print("All source tests passed")