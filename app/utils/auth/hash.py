"""
Hash Utility

Provides a function for generating a SHA-256 hash from a given string.
"""

# --------------------------------------------------------------------------------
# IMPORT LIBRARIES

import hashlib


# --------------------------------------------------------------------------------
# HELPER FUNCTIONS

def hash_str(s: str) -> str:
    """
    Generates a SHA-256 hash for the provided string.

    Args:
        s (str): The input string to hash.

    Returns:
        str: The hexadecimal SHA-256 hash of the input string.
    """
    return hashlib.sha256(s.encode()).hexdigest()
