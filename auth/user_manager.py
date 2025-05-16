import json
import os

# Ensure data/ directory is created relative to this file
USER_DATA_FILE = os.path.join(os.path.dirname(__file__), "../data/users.json")

def load_users():
    if not os.path.exists(USER_DATA_FILE):
        return {}
    with open(USER_DATA_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_users(users):
    # Ensure the data directory exists
    os.makedirs(os.path.dirname(USER_DATA_FILE), exist_ok=True)
    print(f"[DEBUG] Saving to: {USER_DATA_FILE}")  # Debug
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)

def add_user(username, password):
    print(f"[DEBUG] Attempting to register: {username} / {password}")  # Debug
    users = load_users()
    print(f"[DEBUG] Current users: {users}")  # Debug

    if username in users:
        print("[DEBUG] Username already exists.")  # Debug
        return False

    users[username] = password
    save_users(users)
    print(f"[DEBUG] User '{username}' added successfully.")  # Debug
    return True

def check_credentials(username, password):
    users = load_users()
    print(f"[DEBUG] Users loaded: {users}")  # Debug
    return users.get(username) == password
