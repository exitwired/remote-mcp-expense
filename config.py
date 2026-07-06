from pathlib import Path
import json
import os
import controller

# --------------------------------
# local env
# BASE_DIR = Path(__file__).resolve().parent
#
# DATA_DIR = BASE_DIR / "data"
# DATA_DIR.mkdir(parents=True, exist_ok=True)
#
# SESSION_FILE = DATA_DIR / "session.json"

#  Remote server

DATA_DIR = Path(os.getenv("DATA_DIR", "/tmp"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

SESSION_FILE = DATA_DIR / "session.json"
# --------------------------------


if not SESSION_FILE.exists():
    SESSION_FILE.write_text(
        json.dumps({"active_user": None}, indent=4),
        encoding="utf-8",
    )


def set_active_user(username):
    if not controller.user_exists(username):
        return f"User '{username}' does not exist. Please register the user first."

    SESSION_FILE.write_text(
        json.dumps(
            {"active_user": username},
            indent=4,
        ),
        encoding="utf-8",
    )

    return f"Active user is now '{username}'."


def get_active_user():
    data = json.loads(
        SESSION_FILE.read_text(encoding="utf-8")
    )

    return data["active_user"]