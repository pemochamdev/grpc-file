import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI", "sqlite:///payment_system.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
    PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")
    PAYPAL_API_BASE_URL = os.getenv("PAYPAL_API_BASE_URL", "https://api.sandbox.paypal.com")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "test")  # 'test' ou 'production'
