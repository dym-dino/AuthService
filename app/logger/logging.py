"""
Logging Configuration

This module configures a logger to output logs to both the console and PostgreSQL.
"""
# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import logging

import psycopg2

from app.config import settings


# --------------------------------------------------------------------------------
# PostgreSQL Log Handler Class

class PostgresLogHandler(logging.Handler):
    def __init__(self, db_url):
        super().__init__()
        self.conn = psycopg2.connect(db_url)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                level VARCHAR(10),
                message TEXT
            );
        """)
        self.conn.commit()

    def emit(self, record):
        log_entry = self.format(record)
        try:
            self.cursor.execute(
                "INSERT INTO logs (level, message) VALUES (%s, %s);",
                (record.levelname, log_entry)
            )
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Database logging error: {e}")
            self.conn.rollback()

    def close(self):
        self.cursor.close()
        self.conn.close()
        super().close()

    def setup(self):
        self.create_table()


# --------------------------------------------------------------------------------
# LOGGER CONFIGURATION

# LOGGER CONFIGURATION
logger = logging.getLogger("auth_logger")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# PostgreSQL handler
if settings.LOG_TO_DB:
    postgres_handler = PostgresLogHandler(settings.POSTGRES_URL)
    postgres_handler.setLevel(logging.INFO)
    postgres_handler.setFormatter(console_formatter)
    logger.addHandler(postgres_handler)
    postgres_handler.setup()

logger.info("Logger initialized: logs will be sent to both console and PostgreSQL")
