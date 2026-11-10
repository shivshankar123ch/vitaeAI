import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def _read_secret(name: str) -> str | None:
    value = os.getenv(name)
    if value is None:
        return None

    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1].strip()
    return value or None


def _read_positive_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value)
    except ValueError as error:
        raise RuntimeError(f"{name} must be a positive integer.") from error
    if parsed <= 0:
        raise RuntimeError(f"{name} must be a positive integer.")
    return parsed


class Settings:
    PROJECT_NAME = "Placement ERP"
    DATABASE_URL = os.getenv("DATABASE_URL")
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID") or os.getenv("RAZORPAY_API_KEY")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET") or os.getenv(
        "RAZORPAY_API_SECRET_KEY"
    )
    PLAN_ADMIN_USERNAME = os.getenv("PLAN_ADMIN_USERNAME")
    PLAN_ADMIN_PASSWORD = os.getenv("PLAN_ADMIN_PASSWORD")
    PLAN_ADMIN_JWT_SECRET = os.getenv("PLAN_ADMIN_JWT_SECRET")
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = _read_positive_int("SMTP_PORT", 587)
    SMTP_USERNAME = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD = _read_secret("SMTP_PASSWORD")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME")
    OTP_EXPIRE_MINUTES = _read_positive_int("OTP_EXPIRE_MINUTES", 5)
    OTP_SESSION_SECRET = _read_secret("OTP_SESSION_SECRET")
    OTP_COOKIE_SECURE = os.getenv("OTP_COOKIE_SECURE", "false").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not configured. Set it in the project .env file "
            "or in the environment."
        )


settings = Settings()
