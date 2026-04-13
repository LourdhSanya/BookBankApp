"""
Tier 3 – Data Layer
database.py: PostgreSQL connection via psycopg2 (Neon DB).

Strict Object-Oriented Refactor:
Uses a DatabaseConnection class to manage the connection per request.
Tables are auto-created on first startup.
"""

import os
import psycopg2
import psycopg2.extras
from flask import g
from werkzeug.security import generate_password_hash


class DatabaseConnection:
    """Manages database connection lifecycle and initialization using OOP."""

    @staticmethod
    def _get_url():
        url = os.environ.get("DATABASE_URL")
        if not url:
            raise RuntimeError(
                "Missing DATABASE_URL environment variable.\n"
                "Set it in .env (local) or your Vercel dashboard (production)."
            )
        return url

    @classmethod
    def get_connection(cls):
        """Return the per-request DB connection (opened once, reused within request)."""
        if "db" not in g:
            g.db = psycopg2.connect(
                cls._get_url(),
                cursor_factory=psycopg2.extras.RealDictCursor,
            )
            g.db.autocommit = True
        return g.db

    @classmethod
    def close_connection(cls, e=None):
        """Close the per-request DB connection at end of request."""
        db = g.pop("db", None)
        if db is not None:
            db.close()

    @classmethod
    def init_db(cls, app):
        """Create tables (if missing) and seed demo data on first run."""
        with app.app_context():
            cls._create_tables()
            cls._seed_data()

    @classmethod
    def _create_tables(cls):
        db = cls.get_connection()
        with db.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id   SERIAL PRIMARY KEY,
                    username  TEXT NOT NULL UNIQUE,
                    password  TEXT NOT NULL,
                    name      TEXT NOT NULL,
                    role      TEXT NOT NULL CHECK(role IN ('student', 'librarian'))
                );

                CREATE TABLE IF NOT EXISTS books (
                    book_id   SERIAL PRIMARY KEY,
                    book_name TEXT NOT NULL,
                    author    TEXT NOT NULL DEFAULT 'Unknown',
                    status    TEXT NOT NULL DEFAULT 'Available'
                                   CHECK(status IN ('Available', 'Issued', 'Reserved'))
                );

                CREATE TABLE IF NOT EXISTS issues (
                    issue_id    SERIAL PRIMARY KEY,
                    user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    book_id     INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
                    issue_date  DATE          NOT NULL,
                    due_date    DATE          NOT NULL,
                    return_date DATE,
                    fine        NUMERIC(10,2) DEFAULT 0.00
                );

                CREATE TABLE IF NOT EXISTS reservations (
                    reservation_id   SERIAL PRIMARY KEY,
                    book_id          INTEGER NOT NULL REFERENCES books(book_id) ON DELETE CASCADE,
                    user_id          INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
                    reservation_date DATE    NOT NULL
                );
            """)

    @classmethod
    def _seed_data(cls):
        db = cls.get_connection()
        with db.cursor() as cur:
            cur.execute("SELECT user_id FROM users LIMIT 1")
            if cur.fetchone():
                return  # Already seeded

            cur.execute(
                "INSERT INTO users (username, password, name, role) VALUES "
                "(%s,%s,%s,%s), (%s,%s,%s,%s), (%s,%s,%s,%s)",
                (
                    "admin",
                    generate_password_hash("admin123"),
                    "Alice Admin",
                    "librarian",
                    "student1",
                    generate_password_hash("pass123"),
                    "Bob Student",
                    "student",
                    "student2",
                    generate_password_hash("pass456"),
                    "Carol Student",
                    "student",
                ),
            )

            cur.execute(
                "INSERT INTO books (book_name, author) VALUES "
                "(%s,%s), (%s,%s), (%s,%s), (%s,%s), (%s,%s)",
                (
                    "Introduction to Algorithms",
                    "Cormen et al.",
                    "Clean Code",
                    "Robert C. Martin",
                    "The Pragmatic Programmer",
                    "Hunt & Thomas",
                    "Design Patterns",
                    "Gang of Four",
                    "Python Crash Course",
                    "Eric Matthes",
                ),
            )
