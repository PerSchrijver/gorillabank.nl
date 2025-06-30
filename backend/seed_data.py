# backend/seed_utils.py
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import inspect
from models import db, User
from decimal import Decimal
from hashlib import md5

SEED = [
    {
        "full_name": "Barrimus Gerrardimus Linger",
        "email": "b.g.linger@gmail.com",
        "password_hash": md5(b"banana1").hexdigest(),
        "balance": Decimal("124.69"),
    },
    {
        "full_name": "Webbmaster69",
        "email": "webmaster69@hotmail.live",
        "password_hash": md5(b"ImpossiblePassword1!").hexdigest(),
        "balance": Decimal("87455.00"),
    },
    {
        "full_name": "Costco LLC",
        "email": "finance@costco.com",
        "password_hash": md5(b"Another!Hard!Pass").hexdigest(),
        "balance": Decimal("253900.55"),
    },
    {
        "full_name": "Gorilla CEO",
        "email": "ceo@gorillabank.nl",
        "password_hash": md5(b"SuperSecureCEO2025%").hexdigest(),
        "balance": Decimal("1000000.00"),
        "role": "admin",
    },
    {
        "full_name": "Xander Savier <h1>Sorriman",
        "email": "xss@gorillabank.nl",
        "password_hash": md5(b"YetAnotherStrongPass#").hexdigest(),
        "balance": Decimal("9012.85"),
    },
    {
        "full_name": "Test",
        "email": "test@test.test",
        "password_hash": md5(b"test").hexdigest(),
        "balance": Decimal("100.00"),
    },
]

def seed_users_if_needed():
    # Upsert all rows in one round trip
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
