import sqlite3
import os
from pathlib import Path
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

DB_PATH = Path(__file__).resolve().parent / "users.db"


def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create the users table if it doesn't exist."""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                username    TEXT    NOT NULL UNIQUE,
                email       TEXT    NOT NULL UNIQUE,
                password    TEXT    NOT NULL,
                created_at  TEXT    DEFAULT (datetime('now'))
            )
        """)
        conn.commit()


class User(UserMixin):
    """Thin wrapper so flask-login works with raw SQLite rows."""

    def __init__(self, row):
        self.id       = row["id"]
        self.username = row["username"]
        self.email    = row["email"]
        self._password = row["password"]

    @staticmethod
    def get_by_id(user_id: int):
        with get_db() as conn:
            row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_by_email(email: str):
        with get_db() as conn:
            row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        return User(row) if row else None

    @staticmethod
    def get_by_username(username: str):
        with get_db() as conn:
            row = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return User(row) if row else None

    @staticmethod
    def create(username: str, email: str, password: str):
        hashed = generate_password_hash(password)
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, hashed),
            )
            conn.commit()
        return User.get_by_email(email)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self._password, password)
