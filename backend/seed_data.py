# backend/seed_utils.py
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import inspect
from models import db, User
from decimal import Decimal
from passlib.hash import md5_crypt

SEED = [
    {
        "full_name": "Barrimus Gerrardimus Linger",
        "email": "b.g.linger@gmail.com",
        "password_hash": md5_crypt.hash("banana1"),
        "balance": Decimal("124.69"),
    },
    {
        "full_name": "Webbmaster69",
        "email": "webmaster69@hotmail.live",
        "password_hash": md5_crypt.hash("ImpossiblePassword1!"),
        "balance": Decimal("87455.00"),
    },
    {
        "full_name": "Costco LLC",
        "email": "finance@costco.com",
        "password_hash": md5_crypt.hash("Another!Hard!Pass"),
        "balance": Decimal("253900.55"),
    },
    {
        "full_name": "Gorilla CEO",
        "email": "ceo@gorillabank.nl",
        "password_hash": md5_crypt.hash("SuperSecureCEO2025%"),
        "balance": Decimal("1000000.00"),
        "role": "admin",
    },
    {
        "full_name": "Xander Savier <h1>Sorriman",
        "email": "xss@gorillabank.nl",
        "password_hash": md5_crypt.hash("YetAnotherStrongPass#"),
        "balance": Decimal("9012.85"),
    },
    {
        "full_name": "Test",
        "email": "test@test.test",
        "password_hash": md5_crypt.hash("test"),
        "balance": Decimal("100.00"),
    },
]

def seed_users_if_needed():
    # 2. Upsert all rows in one round trip
    stmt = pg_insert(User).values(SEED)
    stmt = stmt.on_conflict_do_nothing(index_elements=["email"])

    # For SQLite fallback (no ON CONFLICT in dialect)
    try:
        db.session.execute(stmt)
    except NotImplementedError:
        # degrade gracefully: loop & skip if exists
        for row in SEED:
            if not User.query.filter_by(email=row["email"]).first():
                db.session.add(User(**row))

    db.session.commit()
