def validate_email(address):
    """Return True if address is a valid email, False otherwise."""
    import re
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return bool(re.match(pattern, address))
