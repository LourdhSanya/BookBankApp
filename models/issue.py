"""
Tier 3 – Data Layer (OOP)
models/issue.py: Manages book issues, returns, and fine calculation using DAOs.
"""

from datetime import date, timedelta
from database import DatabaseConnection
from models.book import BookDAO


class IssueDAO:
    """Data Access Object for Issues."""

    @staticmethod
    def calculate_fine(due_date_raw, return_date_raw=None):
        """
        Fine calculation logic. ₹1 per day overdue.
        """
        due_date = (
            getattr(due_date_raw, "date", lambda: due_date_raw)()
            if hasattr(due_date_raw, "date")
            else due_date_raw
        )

        if return_date_raw:
            return_date_obj = (
                getattr(return_date_raw, "date", lambda: return_date_raw)()
                if hasattr(return_date_raw, "date")
                else return_date_raw
            )
            if return_date_obj > due_date:
                return float((return_date_obj - due_date).days * 1.0)
            return 0.0

        today = date.today()
        if today > due_date:
            return float((today - due_date).days * 1.0)
        return 0.0

    @classmethod
    def issue_book(cls, book_id, user_id):
        """
        Creates an issue record. 14 days loan period.
        """
        db = DatabaseConnection.get_connection()
        issue_date = date.today()
        due_date = issue_date + timedelta(days=14)

        with db.cursor() as cur:
            cur.execute(
                """
                INSERT INTO issues (user_id, book_id, issue_date, due_date)
                VALUES (%s, %s, %s, %s)
                """,
                (user_id, book_id, issue_date, due_date),
            )

        BookDAO.update_status(book_id, "Issued")

    @classmethod
    def get_user_issues(cls, user_id):
        """Get all issues for a specific user (joined with book data)."""
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                cur.execute(
                    """
                    SELECT i.*, b.book_name, b.author
                    FROM issues i
                    JOIN books b ON i.book_id = b.book_id
                    WHERE i.user_id = %s
                    ORDER BY i.issue_date DESC
                    """,
                    (user_id,),
                )
                issues = cur.fetchall()
                for issue in issues:
                    issue["calculated_fine"] = cls.calculate_fine(
                        issue["due_date"], issue["return_date"]
                    )
                    issue["is_overdue"] = issue["calculated_fine"] > 0
                return issues
        except Exception:
            return []

    @classmethod
    def get_all_active_issues(cls):
        """Get all currently active issues (not yet returned)."""
        try:
            db = DatabaseConnection.get_connection()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT i.*, b.book_name, u.username, u.name as user_fullname
                    FROM issues i
                    JOIN books b ON i.book_id = b.book_id
                    JOIN users u ON i.user_id = u.user_id
                    WHERE i.return_date IS NULL
                    ORDER BY i.due_date ASC
                    """)
                issues = cur.fetchall()
                for issue in issues:
                    issue["calculated_fine"] = cls.calculate_fine(
                        issue["due_date"], None
                    )
                    issue["is_overdue"] = issue["calculated_fine"] > 0
                return issues
        except Exception:
            return []

    @classmethod
    def count_overdue(cls):
        """Count the number of non-returned books past their due date."""
        issues = cls.get_all_active_issues()
        return sum(1 for issue in issues if issue["calculated_fine"] > 0)

    @classmethod
    def return_book(cls, issue_id):
        """Record the return of a book and calculate final fine."""
        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute(
                "SELECT book_id, due_date FROM issues WHERE issue_id = %s", (issue_id,)
            )
            record = cur.fetchone()
            if not record:
                raise ValueError("Issue record not found.")

            book_id = record["book_id"]
            due_date = (
                getattr(record["due_date"], "date", lambda: record["due_date"])()
                if hasattr(record["due_date"], "date")
                else record["due_date"]
            )
            return_date = date.today()

            final_fine = 0.0
            if return_date > due_date:
                final_fine = float((return_date - due_date).days * 1.0)

            cur.execute(
                """
                UPDATE issues 
                SET return_date = %s, fine = %s 
                WHERE issue_id = %s
                """,
                (return_date, final_fine, issue_id),
            )

        # Check if requested, otherwise mark available

        db = DatabaseConnection.get_connection()
        with db.cursor() as cur:
            cur.execute(
                "SELECT reservation_id FROM reservations WHERE book_id = %s ORDER BY reservation_date ASC LIMIT 1",
                (book_id,),
            )
            has_reservation = cur.fetchone()

        if has_reservation:
            BookDAO.update_status(book_id, "Reserved")
        else:
            BookDAO.update_status(book_id, "Available")
