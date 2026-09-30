import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_NAME = os.getenv("APP_NAME", "PocketSmart AI")

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "pocketsmart-development-secret-change-this"
    )

    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    GEMINI_MODEL = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )

    HOST = os.getenv(
        "HOST",
        "127.0.0.1"
    )

    PORT = int(
        os.getenv(
            "PORT",
            "8000"
        )
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'pocketsmart.db'}"
    )

    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://127.0.0.1:8000,http://localhost:8000"
        ).split(",")
        if origin.strip()
    ]


settings = Settings()