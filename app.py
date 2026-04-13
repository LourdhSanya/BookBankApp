"""
Tier 2 – Business Logic Layer
app.py: Flask entry point — registers blueprints, teardown, CSRF, and session config.
"""

import os
import sys

# Load .env for local development (no-op if file doesn't exist)
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# Make sure the bookbank/ directory is on the Python path
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, flash, redirect, url_for, session  # noqa: E402
from flask_wtf.csrf import CSRFProtect  # noqa: E402
from database import DatabaseConnection  # noqa: E402
from routes.auth_routes import auth_bp  # noqa: E402
from routes.book_routes import book_bp  # noqa: E402
from routes.issue_routes import issue_bp  # noqa: E402
from routes.reservation_routes import reservation_bp  # noqa: E402

csrf = CSRFProtect()


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # Secret key — required for sessions and CSRF
    app.secret_key = os.environ.get("SECRET_KEY")
    if not app.secret_key:
        raise RuntimeError(
            "Missing SECRET_KEY environment variable.\n"
            "Set it in .env (local) or your Vercel dashboard (production)."
        )

    # CSRF protection for all POST forms
    csrf.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(issue_bp)
    app.register_blueprint(reservation_bp)

    # Close DB connection per-request
    app.teardown_appcontext(DatabaseConnection.close_connection)

    # Create tables and seed data on startup
    DatabaseConnection.init_db(app)

    # ── Global error handlers ──────────────────────────────────────────────
    @app.errorhandler(404)
    def page_not_found(e):
        flash("Page not found.", "danger")
        if "user_id" in session:
            return redirect(url_for("book.index"))
        return redirect(url_for("auth.login"))

    @app.errorhandler(500)
    def internal_error(e):
        flash("Something went wrong. Please try again.", "danger")
        if "user_id" in session:
            return redirect(url_for("book.index"))
        return redirect(url_for("auth.login"))

    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {e}")
        flash("An unexpected error occurred. Please try again.", "danger")
        if "user_id" in session:
            return redirect(url_for("book.index"))
        return redirect(url_for("auth.login"))

    return app


# Module-level app for Vercel serverless & local dev
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
