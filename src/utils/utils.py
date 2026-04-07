import sys
import os

# Add the project root to the system path to allow imports from config.py
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..",".."))
sys.path.append(project_root)

from config import ALLOWED_USER_FIELDS, ALLOWED_ADDRESS_FIELDS, USER_DEFAULT, ADDRESS_DEFAULT

def sanitize_user(user: dict) -> dict:
    sanitized = {}
    
    # Check for unexpected top-level fields
    unexpected_fields = set(user.keys()) - ALLOWED_USER_FIELDS
    if unexpected_fields:
        print(f"Warning: Unexpected fields found in user: {unexpected_fields}")

    for field in ALLOWED_USER_FIELDS:
        if field == "address":
            addr = user.get("address", {})
            # Check for unexpected address fields
            unexpected_addr_fields = set(addr.keys()) - ALLOWED_ADDRESS_FIELDS
            if unexpected_addr_fields:
                print(f"Warning: Unexpected fields in address: {unexpected_addr_fields}")
            
            sanitized["address"] = {k: addr.get(k, ADDRESS_DEFAULT[k]) for k in ALLOWED_ADDRESS_FIELDS}
        else:
            sanitized[field] = user.get(field, USER_DEFAULT[field])
    
    return sanitized