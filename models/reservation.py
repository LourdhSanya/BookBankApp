"""
Tier 3 – Data Layer (OOP)
models/reservation.py: Handles book reservations using Data Access Object pattern.
"""

from datetime import date
from database import DatabaseConnection
from models.book import BookDAO


class ReservationDAO:
    """Data Access Object for Reservations."""

    @classmethod
    def create_reservation(cls, book_id, user_id):
        """Create a reservation for a book."""
        db = DatabaseConnection.get_connection()
        reservation_date = date.today()

        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reservations (book_id, user_id, reservation_date)
                VALUES (%s, %s, %s)
                """,
                (book_id, user_id, reservation_date),
            )

        BookDAO.update_status(book_id, "Reserved")

    @classmethod
    def get_user_reservations(cls, user_id):
        """Get all reservations for a specific user."""
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                cur.execute(
                    """
                    SELECT r.*, b.book_name, b.author, b.status 
                    FROM reservations r
                    JOIN books b ON r.book_id = b.book_id
                    WHERE r.user_id = %s
                    ORDER BY r.reservation_date DESC
                    """,
                    (user_id,),
                )
                return cur.fetchall()
        except Exception:
            return []

    @classmethod
    def get_all_reservations(cls):
        """Get all active reservations."""
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT r.*, b.book_name, b.status, u.username, u.name as user_fullname 
                    FROM reservations r
                    JOIN books b ON r.book_id = b.book_id
                    JOIN users u ON r.user_id = u.user_id
                    ORDER BY r.reservation_date DESC
                    """)
                return cur.fetchall()
        except Exception:
            return []

    @classmethod
    def delete_reservation(cls, reservation_id):
        """Cancel a reservation and potentially free the book."""
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute(
                "SELECT book_id FROM reservations WHERE reservation_id = %s",
                (reservation_id,),
            )
            record = cur.fetchone()
            if not record:
                return

            book_id = record["book_id"]

            # Delete this reservation
            cur.execute(
                "DELETE FROM reservations WHERE reservation_id = %s", (reservation_id,)
            )

            # If the book is completely checked out ("Issued"), we don't mark as available.
            # If the book was "Reserved", let's check if there are OTHER reservations.
            # If no other reservations, and book not issued, revert to Available.

            # Check current status
            cur.execute("SELECT status FROM books WHERE book_id = %s", (book_id,))
            book_status = cur.fetchone()["status"]

            if book_status == "Reserved":
                cur.execute(
                    "SELECT COUNT(*) as count FROM reservations WHERE book_id = %s",
                    (book_id,),
                )
                count = cur.fetchone()["count"]
                if count == 0:
                    BookDAO.update_status(book_id, "Available")

    @classmethod
    def fulfill_reservation(cls, reservation_id):
        """Convert a reservation to an issue."""
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute(
                "SELECT book_id, user_id FROM reservations WHERE reservation_id = %s",
                (reservation_id,),
            )
            res = cur.fetchone()
            if not res:
                raise ValueError("Reservation not found.")

            book_id = res["book_id"]
            user_id = res["user_id"]

        # 1. Issue the book
        from models.issue import IssueDAO

        IssueDAO.issue_book(book_id, user_id)

        # 2. Delete the reservation
        cls.delete_reservation(reservation_id)
