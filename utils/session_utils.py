"""Session persistence utilities."""
import os
import json

SESSION_DIR = os.path.expanduser('~/.label_validator')
SESSION_FILE = os.path.join(SESSION_DIR, 'session.json')


def save_session(data):
    try:
        os.makedirs(SESSION_DIR, exist_ok=True)
        with open(SESSION_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving session: {e}")
        return False


def load_session():
    try:
        if os.path.exists(SESSION_FILE):
            with open(SESSION_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading session: {e}")
    return None


def clear_session():
    try:
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)
        return True
    except Exception as e:
        print(f"Error clearing session: {e}")
        return False


def update_session_index(index):
    session = load_session()
    if session:
        session['current_index'] = index
        save_session(session)
