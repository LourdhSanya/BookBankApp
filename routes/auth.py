"""
Tier 2 – Business Logic Layer
routes/auth.py: Shared authentication decorators.

Import these in any blueprint that needs login/role checks:
    from routes.auth import login_required, librarian_required
"""

from functools import wraps
from flask import session, flash, redirect, url_for


def login_required(f):
    """Redirect to login page if no active session."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)

    return decorated


def librarian_required(f):
    """Redirect non-librarians; also enforces login."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        if session.get("role") != "librarian":
            flash("Access denied. Librarians only.", "danger")
            return redirect(url_for("book.dashboard_student"))
        return f(*args, **kwargs)

    return decorated
