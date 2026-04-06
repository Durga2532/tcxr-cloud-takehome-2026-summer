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
# Run the function to add a new user
# ─────────────────────────────────────────────
if __name__ == "__main__":
    q1_add_new_user()