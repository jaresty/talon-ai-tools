from lib.validators import validate_email


def test_validate_email_rejects_invalid():
    assert validate_email("bad") is False
