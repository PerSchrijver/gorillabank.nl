from flask_sqlalchemy import SQLAlchemy
from hashlib import md5
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Numeric(12, 2), default=0)
    role = db.Column(db.String(20), default="customer")

    def verify_password(self, password):
        return md5(password.encode()).hexdigest() == self.password_hash

class Transfer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_user = db.Column(db.Integer, db.ForeignKey("user.id"))
    to_user = db.Column(db.Integer, db.ForeignKey("user.id"))
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    memo = db.Column(db.Text, default="")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
