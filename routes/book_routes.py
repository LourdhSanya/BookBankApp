"""
Tier 2 – Business Logic Layer
routes/book_routes.py: Book listing, search, dashboards, and librarian CRUD (OOP approach).
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash

from models.book import BookDAO
from models.user import UserDAO
from models.issue import IssueDAO
from models.reservation import ReservationDAO
from routes.auth import login_required, librarian_required

book_bp = Blueprint("book", __name__)


# ── dashboards ────────────────────────────────────────────────────────────────


@book_bp.route("/")
@login_required
def index():
    if session.get("role") == "librarian":
        return redirect(url_for("book.dashboard_librarian"))
    return redirect(url_for("book.dashboard_student"))


@book_bp.route("/dashboard/student")
@login_required
def dashboard_student():
    user_id = session["user_id"]
    issued = IssueDAO.get_user_issues(user_id)
    active_issued = [i for i in issued if not i["return_date"]]
    reservations = ReservationDAO.get_user_reservations(user_id)
    return render_template(
        "dashboard_student.html",
        issued_count=len(active_issued),
        reservation_count=len(reservations),
    )


@book_bp.route("/dashboard/librarian")
@librarian_required
def dashboard_librarian():
    all_books = BookDAO.get_all()
    active_issued = IssueDAO.get_all_active_issues()
    students = UserDAO.get_list_by_role("student")
    overdue = IssueDAO.count_overdue()
    return render_template(
        "dashboard_librarian.html",
        total_books=len(all_books),
        issued_count=len(active_issued),
        student_count=len(students),
        overdue_count=overdue,
    )


# ── book listing / search ─────────────────────────────────────────────────────


@book_bp.route("/books")
@login_required
def books():
    search = request.args.get("search", "").strip()
    all_books = BookDAO.get_all(search if search else None)
    students = (
        UserDAO.get_list_by_role("student")
        if session.get("role") == "librarian"
        else []
    )
    return render_template(
        "books.html", books=all_books, search=search, students=students
    )


# ── librarian CRUD ────────────────────────────────────────────────────────────


@book_bp.route("/books/add", methods=["POST"])
@librarian_required
def add_book_route():
    book_name = request.form.get("book_name", "").strip()
    author = request.form.get("author", "").strip()
    if not book_name or not author:
        flash("Book name and author are required.", "danger")
    else:
        BookDAO.add(book_name, author)
        flash(f"Book '{book_name}' added successfully.", "success")
    return redirect(url_for("book.books"))


@book_bp.route("/books/update/<int:book_id>", methods=["POST"])
@librarian_required
def update_book_route(book_id):
    book_name = request.form.get("book_name", "").strip()
    author = request.form.get("author", "").strip()
    if not book_name or not author:
        flash("Book name and author are required.", "danger")
    else:
        BookDAO.update(book_id, book_name, author)
        flash("Book updated successfully.", "success")
    return redirect(url_for("book.books"))


@book_bp.route("/books/delete/<int:book_id>", methods=["POST"])
@librarian_required
def delete_book_route(book_id):
    book = BookDAO.get_by_id(book_id)
    if book and book["status"] == "Issued":
        flash("Cannot delete a book that is currently issued.", "danger")
    else:
        BookDAO.delete(book_id)
        flash("Book deleted.", "success")
    return redirect(url_for("book.books"))


# ── manage students (librarian) ───────────────────────────────────────────────


@book_bp.route("/manage/students")
@librarian_required
def manage_students():
    students = UserDAO.get_list_by_role("student")
    return render_template("manage_students.html", students=students)


@book_bp.route("/manage/students/add", methods=["POST"])
@librarian_required
def add_student_route():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    name = request.form.get("name", "").strip()
    if not username or not password or not name:
        flash("All fields are required.", "danger")
    elif UserDAO.get_by_username(username):
        flash("Username already exists.", "danger")
    else:
        hashed_pw = generate_password_hash(password)
        UserDAO.create(username, hashed_pw, name, "student")
        flash(f"Student '{name}' added.", "success")
    return redirect(url_for("book.manage_students"))


@book_bp.route("/manage/students/delete/<int:user_id>", methods=["POST"])
@librarian_required
def delete_student_route(user_id):
    UserDAO.delete(user_id)
    flash("Student removed.", "success")
    return redirect(url_for("book.manage_students"))
