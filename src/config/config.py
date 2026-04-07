ALLOWED_USER_FIELDS = {
    "user_id", "first_name", "last_name", "email",
    "role", "address", "phone", "is_active", "last_login"
}

ALLOWED_ADDRESS_FIELDS = {
    "street", "city", "state", "zip_code"
}

ADDRESS_DEFAULT = {
    "street": "Unknown",
    "city": "Unknown",
    "state": "Unknown",
    "zip_code": 0,
}

USER_DEFAULT = {
    "user_id": None,
    "first_name": "Unknown",
    "last_name": "Unknown",
    "email": "unknown@xyz.com",
    "role": "User",
    "address": ADDRESS_DEFAULT,
    "phone": "Unknown",
    "is_active": False,
    "last_login": "1970-01-01T00:00:00Z",
}