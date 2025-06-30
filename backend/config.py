import os

class Config:
    SECRET_KEY = b"SuperSecretKeyForGorillaBank"
    # Pick up DATABASE_URL if it is defined, otherwise use a local SQLite file
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SECURE   = False

class ProductionConfig(Config):
    ENV = "production"

class DevelopmentConfig(Config):
    ENV = "development"
