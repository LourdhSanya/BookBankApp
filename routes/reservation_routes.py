"""
Tier 2 – Business Logic Layer
routes/reservation_routes.py: Reserve and cancel (OOP approach).
"""

from flask import Blueprint, render_template, redirect, url_for, flash, session
from models.reservation import ReservationDAO
from models.book import BookDAO
from routes.auth import login_required

reservation_bp = Blueprint("reservation", __name__)


@reservation_bp.route("/reservations")
@login_required
def reservations():
    """
    GET /reservations
    Student  → own reservations.
    Librarian → all reservations.
    """
    if session.get("role") == "librarian":
        records = ReservationDAO.get_all_reservations()
    else:
        records = ReservationDAO.get_user_reservations(session["user_id"])
    return render_template("reservations.html", records=records)


@reservation_bp.route("/reserve/<int:book_id>", methods=["POST"])
@login_required
def reserve_book_route(book_id):
    """POST /reserve/<book_id> — student reserves a non-available book."""
    if session.get("role") == "librarian":
        flash("Librarians do not need to reserve books.", "info")
        return redirect(url_for("book.books"))

    try:
        book = BookDAO.get_by_id(book_id)
        if not book:
            flash("Book not found.", "danger")
        elif book["status"] == "Available":
            flash(
                "Book is completely available. No need to reserve, you can borrow it directly.",
                "info",
            )
        else:
            ReservationDAO.create_reservation(book_id, session["user_id"])
            flash(
                "Book reserved successfully. You will be notified when it is available.",
                "success",
            )
    except Exception:
        flash("Failed to reserve book.", "danger")

    return redirect(url_for("book.books"))


@reservation_bp.route("/reserve/cancel/<int:reservation_id>", methods=["POST"])
@login_required
def cancel_reservation_route(reservation_id):
    """POST /reserve/cancel/<id> — cancel a reservation."""
    try:
        ReservationDAO.delete_reservation(reservation_id)
        flash("Reservation cancelled.", "success")
    except Exception:
        flash("Failed to cancel reservation.", "danger")

    return redirect(url_for("reservation.reservations"))
