"""Contraseñas con PBKDF2 (nunca en claro)."""

import hashlib
import hmac
import os


def hash_pw(pw):
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 200_000)
    return f"{salt.hex()}:{h.hex()}"


def check_pw(pw, stored):
    try:
        salt_hex, h_hex = stored.split(":")
        h = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(salt_hex), 200_000)
        return hmac.compare_digest(h.hex(), h_hex)
    except (ValueError, AttributeError):
        return False
