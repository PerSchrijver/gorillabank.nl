"""
Vulnerable bank application for a security demo.
"""

import os
import locale
from decimal import Decimal
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.exceptions import HTTPException
from hashlib import md5
from models import db, User, Transfer
from config import ProductionConfig, DevelopmentConfig
from seed_data import seed_users_if_needed


def create_app() -> Flask:
    app = Flask(__name__)

    # ------------------------------------------------------------------
    #  Environment / Config
    # ------------------------------------------------------------------
    assert os.environ["APP_ENV"] in {"production", "development"}, \
        "APP_ENV must be 'production' or 'development'"

    cfg_cls = ProductionConfig if os.environ["APP_ENV"] == "production" else DevelopmentConfig
    app.config.from_object(cfg_cls)

    db.init_app(app)

    if app.config["ENV"] == "development":
        with app.app_context():
            db.create_all()
            seed_users_if_needed()

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    def current_user():
        uid = session.get("uid")
        return User.query.get(uid) if uid else None

    def login_required(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user():
                return redirect(url_for("login"))
            return fn(*args, **kwargs)
        return wrapper

    # Expose current_user to every template
    @app.context_processor
    def inject_user():
        return {"current_user": current_user()}

    # Jinja filter € formatting
    @app.template_filter("eur")
    def format_eur(value):
        try:
            return locale.currency(value, symbol=True, grouping=True)
        except Exception:
            # Fallback if locale fails
            return f"€ {value:,.2f}"

    # ------------------------------------------------------------------
    #  Routes
    # ------------------------------------------------------------------
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            u = User(
                full_name=request.form["full_name"],
                email=request.form["email"],
                password_hash=md5(request.form["password"].encode()).hexdigest(),
            )
            db.session.add(u)
            db.session.commit()
            flash("Account created, please sign in.")
            return redirect(url_for("login"))
        return render_template("register.html")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            email = request.form["email"]
            pw = request.form["password"]
            user = User.query.filter_by(email=email).first()
            if user and user.verify_password(pw):
                session["uid"] = user.id
                flash(f"Welcome back, {user.full_name}!")
                return redirect(url_for("dashboard"))
            flash("Invalid credentials", "error")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        session.pop("uid", None)
        flash("You have been logged out.")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        recent = (
            Transfer.query.filter(
                (Transfer.from_user == user.id) | (Transfer.to_user == user.id)
            )
            .order_by(Transfer.timestamp.desc())
            .limit(5)
            .all()
        )
        return render_template("dashboard.html", recent=recent)

    @app.route("/transfer", methods=["POST"])
    @login_required
    def transfer():
        user = current_user()
        to_id = int(request.form["to_user"])
        amount = Decimal(request.form["amount"])
        memo = request.form.get("memo", "")

        if amount <= 0:
            flash("Positive amounts only.")
            return redirect(url_for("dashboard"))

        to_user = User.query.get_or_404(to_id)
        if user.balance < amount:
            flash("Insufficient funds.")
            return redirect(url_for("dashboard"))

        ## Nice race condition (intentional for this demo)
        user.balance -= amount
        to_user.balance += amount
        db.session.add(Transfer(from_user=user.id, to_user=to_id, amount=amount, memo=memo))
        db.session.commit()
        flash("Transfer complete.")
        return redirect(url_for("dashboard"))

    # ------------------------------------------------------------------
    #  Error handlers
    # ------------------------------------------------------------------
    @app.errorhandler(HTTPException)
    def handle_http_error(err: HTTPException):
        app.logger.warning("HTTP error %s: %s", err.code, err.description)
        return render_template("error.html", code=err.code, message=err.description), err.code

    # ------------------------------------------------------------------
    #  Dev-only debug endpoint
    # ------------------------------------------------------------------
    if app.config["ENV"] == "development":

        @app.route("/debug/users")
        def debug_users():
            users = [
                {
                    "id": u.id,
                    "full_name": u.full_name,
                    "email": u.email,
                    "password_hash": u.password_hash,
                    "balance": float(u.balance),
                }
                for u in User.query.all()
            ]
            return jsonify(users)

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.environ["FLASK_RUN_PORT"]))
