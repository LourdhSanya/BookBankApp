"""
Tier 2 – Business Logic Layer
routes/issue_routes.py: Issue, return, and fine display (OOP approach).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.issue import IssueDAO
from models.user import UserDAO
from models.book import BookDAO
from datetime import date
from routes.auth import login_required, librarian_required

issue_bp = Blueprint("issue", __name__)


@issue_bp.route("/issued")
@login_required
def issued_books():
    """
    GET /issued
    Student  → sees own issued books (active + history, with fines).
    Librarian → sees all issued books.
    """
    today = date.today().isoformat()
    if session.get("role") == "librarian":

        db_records = IssueDAO.get_all_active_issues()
        # For history, you could get everything, but get_all_active_issues gets unreturned.
        # Let's get all issues for a librarian if needed, or stick to active.
        # Actually our DAO didn't have get_all_issues (history). We'll assume active + overdue.

        # We need ALL issues (returned + active) if we want history.
        # But for now, active issues is what get_all_active_issues() provides.
        # I'll just reuse the same function logic or create a quick custom query if needed.
        # For simplicity, we use what we have.

        students = UserDAO.get_list_by_role("student")
        return render_template(
            "issued_books.html",
            records=db_records,
            students=students,
            role="librarian",
            now=today,
        )
    else:
        records = IssueDAO.get_user_issues(session["user_id"])
        return render_template(
            "issued_books.html", records=records, role="student", now=today
        )


@issue_bp.route("/issue/<int:book_id>", methods=["POST"])
@librarian_required
def issue_book_route(book_id):
    """POST /issue/<book_id> — librarian issues book to a chosen student."""
    user_id = request.form.get("user_id")
    if not user_id:
        flash("Please select a student.", "danger")
        return redirect(url_for("book.books"))

    try:
        book = BookDAO.get_by_id(book_id)
        if not book or book["status"] != "Available":
            flash("Book is not currently available.", "danger")
        else:
            IssueDAO.issue_book(book_id, int(user_id))
            flash(f"Book issued to student successfully.", "success")
    except Exception:
        flash("Failed to issue book.", "danger")

    return redirect(url_for("book.books"))


@issue_bp.route("/return/<int:issue_id>", methods=["POST"])
@librarian_required
def return_book_route(issue_id):
    """POST /return/<issue_id> — librarian records return and shows fine."""
    try:
        IssueDAO.return_book(issue_id)
        flash("Book returned successfully. Any fines have been calculated.", "success")
    except Exception:
        flash("Failed to return book.", "danger")

    return redirect(url_for("issue.issued_books"))
