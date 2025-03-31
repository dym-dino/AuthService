"""
Automatic Backups

Schedules PostgreSQL backups using pg_dump.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import os
import subprocess
from datetime import datetime

from app.config import settings
from app.logger import logger


# --------------------------------------------------------------------------------
# BACKUP CONFIGURATION
def run_backup():
    """
    Creates a compressed PostgreSQL backup using pg_dump.
    Keeps only the last 10 backups in BACKUP_PATH.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(settings.BACKUP_PATH, f"pg_backup_{timestamp}.sql.gz")

    os.makedirs(settings.BACKUP_PATH, exist_ok=True)

    cmd = [
        "pg_dump",
        f"--dbname={settings.POSTGRES_URL}",
        "--no-password"
    ]

    try:
        with open(backup_file, "wb") as f:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE)
            subprocess.run(["gzip"], stdin=subprocess.PIPE, stdout=f)
        logger.info(f"Backup created: {backup_file}")
    except Exception as e:
        logger.error(f"Backup failed: {e}")

    # Cleanup: keep last 10 backups
    backups = sorted([
        f for f in os.listdir(settings.BACKUP_PATH)
        if f.startswith("pg_backup_") and f.endswith(".sql.gz")
    ])
    for old in backups[:-10]:
        try:
            os.remove(os.path.join(settings.BACKUP_PATH, old))
            logger.info(f"Old backup removed: {old}")
        except Exception as e:
            logger.warning(f"Failed to remove backup {old}: {e}")
