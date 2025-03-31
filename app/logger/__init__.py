"""
Logger Module

Provides logging utilities for the application.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import logging

from ..config import settings

# --------------------------------------------------------------------------------
# MAIN LOGIC

if not settings.TESTING:
    from .logging import logger, postgres_handler

else:
    class NullLogger:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None


    class EmptyLogger(logging.Handler):
        def __init__(self, db_url):
            super().__init__()

        def emit(self, record):
            print(record)

        def close(self):
            super().close()

        def setup(self):
            pass


    logger = NullLogger()
    postgres_handler = EmptyLogger('...')
