# backend/seed_utils.py
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import inspect
from models import db, User, Transfer
from decimal import Decimal
from hashlib import sha256
from datetime import datetime, timedelta
import random
import os

SEED_USERS = [
    {
        "full_name": "Gorilla CEO",
        "email": "ceo@gorillabank.nl",
        "password_hash": sha256(b"SuperSecureCEO2025%1231231231").hexdigest(),
        "balance": Decimal("1000000.00"),
        "role": "admin",
    },
    {
        "full_name": "Xander Savier <h1>Sorriman",
        "email": "xss@gorillabank.nl",
        "password_hash": sha256(b"YetAnotherStrongPass#123123123").hexdigest(),
        "balance": Decimal("9012.85"),
    },
    {
        "full_name": "Costco LLC",
        "email": "finance@costco.com",
        "password_hash": sha256(b"Another!Hard!Pass1127390128301").hexdigest(),
        "balance": Decimal("253900.55"),
    },
    {
        "full_name": "Webbmaster69",
        "email": "webmaster69@hotmail.live",
        "password_hash": sha256(b"ImpossiblePassword11723128973!").hexdigest(),
        "balance": Decimal("87455.00"),
    },
    {
        "full_name": "Barrimus Gerrardimus Linger",
        "email": "b.g.linger@gmail.com",
        "password_hash": sha256(b"banana69").hexdigest(),
        "balance": Decimal("124.69"),
    },
]

SEED_TRANSACTIONS = [
    # Gorilla CEO (admin)
    {
        "from_email": "ceo@gorillabank.nl",
        "to_email": "xss@gorillabank.nl",
        "amount": Decimal("5000.00"),
        "memo": "Startup bonus for XSS specialist",
        "timestamp": datetime.utcnow() - timedelta(days=30),
    },
    {
        "from_email": "ceo@gorillabank.nl",
        "to_email": "finance@costco.com",
        "amount": Decimal("100000.00"),
        "memo": "Bulk banking infrastructure contract",
        "timestamp": datetime.utcnow() - timedelta(days=25),
    },
    {
        "from_email": "ceo@gorillabank.nl",
        "to_email": "b.g.linger@gmail.com",
        "amount": Decimal("50.00"),
        "memo": "Intern crypto test",
        "timestamp": datetime.utcnow() - timedelta(days=10),
    },

    # Xander Savier
    {
        "from_email": "xss@gorillabank.nl",
        "to_email": "webmaster69@hotmail.live",
        "amount": Decimal("123.45"),
        "memo": "<script>alert('bonus');</script>",
        "timestamp": datetime.utcnow() - timedelta(days=12),
    },
    {
        "from_email": "xss@gorillabank.nl",
        "to_email": "ceo@gorillabank.nl",
        "amount": Decimal("1.00"),
        "memo": "Testing fraud detection",
        "timestamp": datetime.utcnow() - timedelta(days=2),
    },
    {
        "from_email": "xss@gorillabank.nl",
        "to_email": "b.g.linger@gmail.com",
        "amount": Decimal("25.00"),
        "memo": "<script>alert('thanks for testing XSSes, memo's are now secure!');</script>",
        "timestamp": datetime.utcnow() - timedelta(days=3),
    },

    # Costco LLC
    {
        "from_email": "finance@costco.com",
        "to_email": "webmaster69@hotmail.live",
        "amount": Decimal("999.99"),
        "memo": "Consulting fee",
        "timestamp": datetime.utcnow() - timedelta(days=15),
    },
    {
        "from_email": "finance@costco.com",
        "to_email": "ceo@gorillabank.nl",
        "amount": Decimal("25000.00"),
        "memo": "Refund for contract overpayment",
        "timestamp": datetime.utcnow() - timedelta(days=8),
    },
    {
        "from_email": "finance@costco.com",
        "to_email": "b.g.linger@gmail.com",
        "amount": Decimal("100.00"),
        "memo": "Employee reward points cashout",
        "timestamp": datetime.utcnow() - timedelta(days=1),
    },

    # Webbmaster69
    {
        "from_email": "webmaster69@hotmail.live",
        "to_email": "ceo@gorillabank.nl",
        "amount": Decimal("500.00"),
        "memo": "Server fees",
        "timestamp": datetime.utcnow() - timedelta(days=20),
    },
    {
        "from_email": "webmaster69@hotmail.live",
        "to_email": "finance@costco.com",
        "amount": Decimal("450.00"),
        "memo": "Hosting refund",
        "timestamp": datetime.utcnow() - timedelta(days=6),
    },
    {
        "from_email": "webmaster69@hotmail.live",
        "to_email": "xss@gorillabank.nl",
        "amount": Decimal("66.66"),
        "memo": "Monthly sub plan",
        "timestamp": datetime.utcnow() - timedelta(days=4),
    },

    # Barrimus Gerrardimus Linger
    {
        "from_email": "b.g.linger@gmail.com",
        "to_email": "ceo@gorillabank.nl",
        "amount": Decimal("10.00"),
        "memo": "Beta test feedback incentive",
        "timestamp": datetime.utcnow() - timedelta(days=28),
    },
    {
        "from_email": "b.g.linger@gmail.com",
        "to_email": "webmaster69@hotmail.live",
        "amount": Decimal("15.69"),
        "memo": "Thanks for the memes",
        "timestamp": datetime.utcnow() - timedelta(days=9),
    },
    {
        "from_email": "b.g.linger@gmail.com",
        "to_email": "xss@gorillabank.nl",
        "amount": Decimal("12.34"),
        "memo": "Bug bounty",
        "timestamp": datetime.utcnow() - timedelta(days=5),
    },
]


if os.environ["FLASK_ENV"] == "development":
    SEED_USERS.append({
        "full_name": "Test",
        "email": "test@test.test",
        "password_hash": sha256(b"test").hexdigest(),
        "balance": Decimal("100.00"),
    })

    SEED_TRANSACTIONS.extend([
        {
        "from_email": "test@test.test",
        "to_email": "xss@gorillabank.nl",
        "amount": Decimal("12.34"),
        "memo": "Bug bounty",
        "timestamp": datetime.utcnow() - timedelta(days=8),
    },
    {
        "from_email": "test@test.test",
        "to_email": "xss@gorillabank.nl",
        "amount": Decimal("14.01"),
        "memo": "Escaped",
        "timestamp": datetime.utcnow() - timedelta(days=5),
    },])

def seed_users_if_needed():
    for row in SEED_USERS:
        if not User.query.filter_by(email=row["email"]).first():
            db.session.add(User(**row))

    for row in SEED_TRANSACTIONS:
        from_user = User.query.filter_by(email=row["from_email"]).first()
        to_user = User.query.filter_by(email=row["to_email"]).first()
        if from_user and to_user:
            transfer = Transfer(
                from_user_id=from_user.id,
                to_user_id=to_user.id,
                amount=row["amount"],
                memo=row["memo"],
                timestamp=row["timestamp"],
            )
            db.session.add(transfer)
        else:
            print(f"Skipping transfer from {row['from_email']} to {row['to_email']} - user not found")
            assert False, f"User not found for transfer from {row['from_email']} to {row['to_email']}"

    db.session.commit()
