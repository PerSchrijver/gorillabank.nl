from models import db, User
from passlib.hash import bcrypt, md5_crypt

SEED = [
    {
        "full_name": "Barrimus Gerrardimus Linger",
        "email": "barrimus@gorillabank.nl",
        "password_hash": md5_crypt.hash("banana1"),
        "balance": 124.69,
    },
    {
        "full_name": "Webbmaster69",
        "email": "webmaster69@gorillabank.nl",
        "password_hash": bcrypt.hash("ImpossiblePassword1!"),
        "balance": 87455.00,
    },
    {
        "full_name": "Costco LLC",
        "email": "accounts@costco.nl",
        "password_hash": bcrypt.hash("Another!Hard!Pass"),
        "balance": 253900.55,
    },
    {
        "full_name": "Gorilla CEO",
        "email": "ceo@gorillabank.nl",
        "password_hash": bcrypt.hash("SuperSecureCEO2025%"),
        "balance": 1000000.00,
        "role": "admin",
    },
    {
        "full_name": "Xander Savier <h1>Sorriman",
        "email": "xss@gorillabank.nl",
        "password_hash": bcrypt.hash("YetAnotherStrongPass#"),
        "balance": 9012.85,
    },
]

def run():
    from app import create_app
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        for entry in SEED:
            db.session.add(User(**entry))
        db.session.commit()
        print("Seeded users \u2705")

if __name__ == "__main__":
    run()
