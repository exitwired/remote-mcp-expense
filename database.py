from pathlib import Path
import sqlite3




# -------------------
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH1 = BASE_DIR / "data" / "expenses.db"

print(DB_PATH1)

# -------------------

from pathlib import Path

test = Path("/app/test.txt")

test.write_text("hello")

print(test.read_text())


# -------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "expenses.db"


# # -------------------
#
# from pathlib import Path
#
# test = Path("/tmp/test.txt")
#
# test.write_text("hello")
#
# print(test.read_text())
#
# # -------------------
#
# import os
# from pathlib import Path
#
# DATA_DIR = Path(os.getenv("DATA_DIR", "/tmp"))
# DATA_DIR.mkdir(exist_ok=True)
#
# DB_FILE = DATA_DIR / "expenses.db"
# # -------------------



def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses
       (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           user_id INTEGER NOT NULL,
           title TEXT NOT NULL,
           amount REAL NOT NULL,
           category TEXT NOT NULL,
           expense_date TEXT NOT NULL,
           created_at TEXT NOT NULL,
           FOREIGN KEY(user_id) REFERENCES users (id))
       """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expense_edit_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        expense_id INTEGER,
        new_title TEXT,
        new_amount REAL,
        new_category TEXT,
        status TEXT DEFAULT 'Pending',
        requested_at TEXT,
        approved_at TEXT
    )
    """)

    conn.commit()
    conn.close()

