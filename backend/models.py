from flask_sqlalchemy import SQLAlchemy
from hashlib import sha256
from datetime import datetime
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(12, 2), default=0)
    role = db.Column(db.String(20), nullable=False)

    def verify_password(self, password):
        print("Checking password for user:", self.email)
        print("Password hash:", self.password_hash)
        print("Password provided:", password)
        print("sha256 of password provided:", sha256(password.encode()).hexdigest())
        return sha256(password.encode()).hexdigest() == self.password_hash

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    to_user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    memo = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    from_user_relationship = relationship("User", foreign_keys=[from_user_id])
    to_user_relationship = relationship("User", foreign_keys=[to_user_id])
