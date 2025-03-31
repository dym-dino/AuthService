"""
Config Settings

Module for loading application configuration settings from a .env file.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES


import os
from pathlib import Path

from dotenv import load_dotenv

# --------------------------------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES

load_dotenv()


# --------------------------------------------------------------------------------
# CONFIGURATION CLASS
class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "default-secret")
    ADMIN_SWAGGER_PASSWORD: str = os.getenv("ADMIN_SWAGGER_PASSWORD", "admin_pass")
    ADMIN_SWAGGER_LOGIN: str = os.getenv("ADMIN_SWAGGER_LOGIN", "admin_login")

    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "auth_db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "auth_user")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    BACKUP_PATH: str = os.getenv("BACKUP_PATH", "/app/backups")

    DOCS_DIR: Path = Path(__file__).resolve().parent.parent / "docs/html"

    LOG_TO_DB: bool = os.getenv("LOG_TO_DB", "true").lower() == "true"

    TESTING: bool = False


# --------------------------------------------------------------------------------
# INSTANTIATE SETTINGS

settings = Settings()
