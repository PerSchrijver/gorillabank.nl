import os

class Config:
    SECRET_KEY = "change-me"
    SQLALCHEMY_DATABASE_URI = "sqlite:///gorillabank.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True

class ProductionConfig(Config):
    ENV = "production"

class DevelopmentConfig(Config):
    ENV = "development"
