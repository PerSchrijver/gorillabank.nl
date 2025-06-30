from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from models import db, User, Transfer
from config import ProductionConfig, DevelopmentConfig
from decimal import Decimal
from werkzeug.exceptions import HTTPException
import os
from functools import wraps
from passlib.hash import md5_crypt
from seed_data import seed_users_if_needed

def create_app():
    app = Flask(__name__)

    assert os.environ["APP_ENV"] in ["production", "development"], "APP_ENV must be 'production' or 'development'"
    IS_DEVELOPMENT = os.environ["APP_ENV"] == "development"
    IS_PRODUCTION = os.environ["APP_ENV"] == "production"
    cfg = ProductionConfig if IS_PRODUCTION else DevelopmentConfig
    app.config.from_object(cfg)

    db.init_app(app)

    if IS_DEVELOPMENT:
        with app.app_context():
            seed_users_if_needed()

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

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            fn = request.form["full_name"]
            email = request.form["email"]
            pw = request.form["password"]
            phash = md5_crypt.hash(pw)
            u = User(full_name=fn, email=email, password_hash=phash)
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
                return redirect("/dashboard")
            flash("Invalid credentials", "error")
        return render_template("login.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        user = current_user()
        welcome = request.args.get("welcome", "")
        recent = Transfer.query.filter(
            (Transfer.from_user == user.id) | (Transfer.to_user == user.id)
        ).order_by(Transfer.timestamp.desc()).limit(5)
        return render_template("dashboard.html", user=user, recent=recent, welcome=welcome)

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

        user.balance -= amount
        to_user.balance += amount
        db.session.add(Transfer(from_user=user.id, to_user=to_id, amount=amount, memo=memo))
        db.session.commit()
        flash("Transfer complete.")
        return redirect(url_for("dashboard"))

    @app.errorhandler(HTTPException)
    def handle_http_error(err: HTTPException):
        """
        Catches any Werkzeug-raised HTTP errors like 404, 403, 401, etc.
        """
        app.logger.warning("HTTP error %s: %s", err.code, err.description)
        return (
            render_template("error.html", code=err.code, message=err.description),
            err.code,
        )

    if cfg.ENV == "development":
        @app.route("/debug/users")
        def debug_users():
            users = [{
                "id": u.id,
                "full_name": u.full_name,
                "email": u.email,
                "password_hash": u.password_hash,
                "balance": float(u.balance)
            } for u in User.query.all()]
            return jsonify(users)

    return app

if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.getenv("FLASK_RUN_PORT")))
