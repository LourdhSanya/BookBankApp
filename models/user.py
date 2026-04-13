"""
Tier 3 – Data Layer (OOP)
models/user.py: CRUD for the users table using Data Access Object pattern.
"""

from database import DatabaseConnection


class UserDAO:
    """Data Access Object for Users."""

    @classmethod
    def get_by_username(cls, username):
        """Fetch a user record by username."""
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE username = %s LIMIT 1", (username,)
                )
                return cur.fetchone()
        except Exception:
            return None

    @classmethod
    def get_list_by_role(cls, role):
        """Fetch all users matching a specific role."""
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM users WHERE role = %s ORDER BY name", (role,)
                )
                return cur.fetchall()
        except Exception:
            return []

    @classmethod
    def count_by_role(cls, role):
        """Count the number of users matching a specific role."""
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as count FROM users WHERE role = %s", (role,)
                )
                row = cur.fetchone()
                return row["count"] if row else 0
        except Exception:
            return 0

    @classmethod
    def create(cls, username, password_hash, name, role):
        """Insert a new user."""
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password, name, role) VALUES (%s, %s, %s, %s)",
                (username, password_hash, name, role),
            )

    @classmethod
    def delete(cls, user_id):
        """Delete a user and cascade their issues/reservations."""
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
