from filters import title_matches, location_matches, too_much_experience, is_clearance

def test_title_matches():
    assert title_matches("Software Engineer, Backend") == True
    assert title_matches("Senior Software Engineer") == False
    assert title_matches("Data Engineer") == True
    assert title_matches("Engineering Manager") == False
    assert title_matches("Account Executive") == False
    assert title_matches("Staff Infrastructure Engineer") == False
    assert title_matches("Capital Markets Analyst") == False
    assert title_matches("Software Engineer Stf - E4") == False
    assert title_matches("Software Engineer - E2") == True

def test_location_matches():
    assert location_matches("New York City, NY") == True
    assert location_matches("Remote-Friendly, United States") == True
    assert location_matches("San Francisco, CA | New York City, NY") == True
    assert location_matches("London, UK") == False
    assert location_matches("Lithuania - Remote") == False
    assert location_matches("Remote-Friendly (Travel Required) | Canada") == False
    assert location_matches("Virtual Three, TX | Remote") == True
    assert location_matches("Remote") == True


def test_too_much_experience():
    assert too_much_experience("5+ years of experience") == True
    assert too_much_experience("minimum of 7 years") == True
    assert too_much_experience("10 years of experience") == True
    assert too_much_experience("five years of experience") == True
    assert too_much_experience("5 or more years") == True
    assert too_much_experience("3+ years of experience") == False
    assert too_much_experience("2-4 years of experience") == False
    assert too_much_experience("no experience required") == False


def test_is_clearance():
    assert is_clearance("Active Secret clearance required") == True
    assert is_clearance("Executive Secretary") == False
    assert is_clearance("Python and AWS") == False