"""
Tier 3 – Data Layer (OOP)
models/book.py: CRUD for the books table via psycopg2 using Data Access Object pattern.
"""

from database import DatabaseConnection


class BookDAO:
    """Data Access Object for Books."""

    @classmethod
    def get_all(cls, search=None):
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                if search:
                    cur.execute(
                        "SELECT * FROM books WHERE book_name ILIKE %s OR author ILIKE %s ORDER BY book_name",
                        (f"%{search}%", f"%{search}%"),
                    )
                else:
                    cur.execute("SELECT * FROM books ORDER BY book_name")
                return cur.fetchall()
        except Exception:
            return []

    @classmethod
    def get_by_id(cls, book_id):
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM books WHERE book_id = %s", (book_id,))
                return cur.fetchone()
        except Exception:
            return None

    @classmethod
    def add(cls, book_name, author):
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO books (book_name, author, status) VALUES (%s, %s, 'Available')",
                (book_name, author),
            )

    @classmethod
    def update(cls, book_id, book_name, author):
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE books SET book_name = %s, author = %s WHERE book_id = %s",
                (book_name, author, book_id),
            )

    @classmethod
    def delete(cls, book_id):
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute("DELETE FROM books WHERE book_id = %s", (book_id,))

    @classmethod
    def update_status(cls, book_id, status):
        """status must be one of: 'Available', 'Issued', 'Reserved'."""
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute(
                "UPDATE books SET status = %s WHERE book_id = %s",
                (status, book_id),
            )

    @classmethod
    def check_availability(cls, book_id):
        book = cls.get_by_id(book_id)
        return book and book["status"] == "Available"
