import json
from datetime import datetime

USER_FILE = "data/userData.json"
NEW_USER_FILE = "data/newUser.json"

# Helper function to load user data from a JSON file
def load_user_data():
    with open(USER_FILE, "r") as f:
        data=json.load(f)
        return data["users"]

# Helper function to save user data to a JSON file
def save_user_data(data):
    with open(USER_FILE, "w") as f:
        json.dump({"users": data}, f, indent=2)

# ─────────────────────────────────────────────
# Q1: Add a new user to the system
# ─────────────────────────────────────────────
def q1_add_new_user(new_user_file=NEW_USER_FILE):
    # Load existing user data
    user_data = load_user_data()

    # Load new user data from the provided JSON file
    with open(new_user_file, "r") as f:
        new_user = json.load(f)

    # Check if the new user's email already exists in the system
    if any(user["email"] == new_user["email"] for user in user_data):
        print(f"Error: A user with email {new_user['email']} already exists.")
        return

    # Add the new user to the list
    user_data.append(new_user)

    # Save the updated user data back to the JSON file
    save_user_data(user_data)
    print(f"New user {new_user['first_name']} {new_user['last_name']} added successfully.")
    
# ─────────────────────────────────────────────
# Q2: Who was the last person to access the system
# ─────────────────────────────────────────────
def q2_last_accessed_user():
    user_data = load_user_data()

    # Only consider active users
    active_users = [
        u for u in user_data 
        if u["is_active"] and u.get("last_login") is not None]

    if not active_users:
        print("No active users found.")
        return

    last_user = max(
        active_users,
        key=lambda u: datetime.strptime(u["last_login"], "%Y-%m-%dT%H:%M:%SZ")
    )

    print(f"Last person to access the system:")
    print(f"  Name       : {last_user['first_name']} {last_user['last_name']}")
    print(f"  Email      : {last_user['email']}")
    print(f"  Role       : {last_user['role']}")
    print(f"  Last Login : {last_user['last_login']}")
    
# ─────────────────────────────────────────────
# Run the function to add a new user
# ─────────────────────────────────────────────
if __name__ == "__main__":
    q1_add_new_user()
    q2_last_accessed_user()
    