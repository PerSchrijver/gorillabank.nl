"""
Vulnerable bank application for a security demo.
"""

import os
import locale
from decimal import Decimal
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.exceptions import HTTPException
from hashlib import sha256
from models import db, User, Transfer
from config import ProductionConfig, DevelopmentConfig
from seed_data import seed_data


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
            # db.drop_all()
            db.create_all()
            # seed_data()

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
            if not request.form["full_name"] or not request.form["email"] or not request.form["password"]:
                flash("All fields are required.", "error")
                return redirect(url_for("register"))
            if len(request.form["full_name"]) < 3:
                flash("Full name must be at least 3 characters.", "error")
                return redirect(url_for("register"))
            if len(request.form["full_name"]) > 200:
                flash("Full name must be at most 200 characters.", "error")
                return redirect(url_for("register"))
            if len(request.form["email"]) < 5 or "@" not in request.form["email"] or len(request.form["email"]) > 100:
                flash("Invalid email address.", "error")
                return redirect(url_for("register"))

            u = User(
                full_name=request.form["full_name"],
                email=request.form["email"],
                password_hash=sha256(request.form["password"].encode()).hexdigest(),
            )
            db.session.add(u)
            db.session.commit()
            session["uid"] = u.id
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
                print("Logged in user:", user.full_name, "with ID:", user.id)
                return redirect(url_for("dashboard"))
            flash("Invalid credentials", "error")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        session.pop("uid", None)
        flash("You have been logged out.", "success")
        return redirect(url_for("index"))

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        recent = (
            Transfer.query.filter(
                (Transfer.from_user_id == user.id) | (Transfer.to_user_id == user.id)
            )
            .order_by(Transfer.timestamp.desc())
            .limit(8)
            .all()
        )
        return render_template("dashboard.html", recent=recent)

    @app.route("/transfer", methods=["POST"])
    @login_required
    def transfer():
        from_user = current_user()
        to_user_email = request.form["to_user_email"]
        amount = Decimal(request.form["amount"])
        memo = request.form.get("memo", "")

        if amount <= 0:
            flash("Positive amounts only.", "error")
            return redirect(url_for("dashboard"))

        to_user = User.query.filter_by(email=to_user_email).first()
        if to_user is None:
            flash("User not found.", "error")
            return redirect(url_for("dashboard"))
        if from_user.balance < amount:
            flash("Insufficient funds.", "error")
            return redirect(url_for("dashboard"))

        ## Nice race condition (intentional for this demo)
        from_user.balance -= amount
        to_user.balance += amount
        db.session.add(Transfer(from_user_id=from_user.id, to_user_id=to_user.id, amount=amount, memo=memo))
        db.session.commit()
        flash("Transfer complete.", "success")
        print("Transfer from user ID:", from_user.id, "to user ID:", to_user.id, "amount:", amount, "memo:", memo)
        return redirect(url_for("dashboard"))

    @app.route("/admin", methods=["GET", "POST"])
    @login_required
    def admin():
        user = current_user()
        if not user.role == "admin":
            flash("Access denied.", "error")
            return redirect(url_for("index"))

        if request.method == "POST":
            action = request.form.get("action")
            target_user_id = request.form.get("user_id")

            target_user = User.query.get(target_user_id)
            if not target_user:
                flash("Target user not found.", "error")
                return redirect(url_for("admin"))

            if action == "delete":
                if target_user.id == user.id:
                    flash("You cannot delete your own account.", "error")
                    return redirect(url_for("admin"))

                raise NotImplementedError("User deletion is not implemented in this demo. Would cause issues with transfers.")

            elif action == "add_funds":
                money = request.form.get("money")
                if not money or not money.isdigit():
                    flash("Invalid amount.", "error")
                    return redirect(url_for("admin"))

                ## Add money to target user
                money = Decimal(money)
                target_user.balance += money
                db.session.commit()
            
            else:
                flash("Unknown action.", "error")
                return redirect(url_for("admin"))

        users = User.query.all()
        users.sort(key=lambda u: u.id)
        return render_template("admin.html", users=users)

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
        @app.route("/api/user/<int:user_id>")
        def debug_user(user_id):
            u = User.query.get_or_404(user_id)
            user_data = {
                "id": u.id,
                "full_name": u.full_name,
                "email": u.email,
                "password_hash": u.password_hash,
                "balance": float(u.balance),
            }
            return jsonify(user_data)

        ## Hidden endpoint used for development, not actually part of the challenge
        @app.route("/remake_db")
        def remake_db():
            db.drop_all()
            db.create_all()
            seed_data()
            return "Database recreated and seeded."

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.environ["FLASK_RUN_PORT"]))
