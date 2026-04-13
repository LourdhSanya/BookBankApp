"""
Tier 2 – Business Logic Layer
routes/auth_routes.py: Login, registration, and logout (OOP).
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
from models.user import UserDAO

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return _redirect_dashboard()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = UserDAO.get_by_username(username)
        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["user_id"]
            session["username"] = user["username"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['name']}!", "success")
            return _redirect_dashboard()
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return _redirect_dashboard()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not username or not password:
            flash("All fields are required.", "danger")
        elif len(username) < 3:
            flash("Username must be at least 3 characters.", "danger")
        elif len(password) < 4:
            flash("Password must be at least 4 characters.", "danger")
        elif password != confirm_password:
            flash("Passwords do not match.", "danger")
        elif UserDAO.get_by_username(username):
            flash("Username already taken. Please choose another.", "danger")
        else:
            try:
                hashed_pw = generate_password_hash(password)
                UserDAO.create(username, hashed_pw, name, "student")
                flash("Account created successfully! Please sign in.", "success")
                return redirect(url_for("auth.login"))
            except Exception:
                flash("Something went wrong. Please try again.", "danger")

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


def _redirect_dashboard():
    if session.get("role") == "librarian":
        return redirect(url_for("book.dashboard_librarian"))
    return redirect(url_for("book.dashboard_student"))
