"""
Rate Limiting

Provides global rate limiting configuration using slowapi.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES


from slowapi import Limiter
from slowapi.util import get_remote_address

# --------------------------------------------------------------------------------
# CONFIGURATION

limiter = Limiter(key_func=get_remote_address)
