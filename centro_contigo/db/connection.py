"""Conexión a SQLite que siempre se cierra."""

import sqlite3
from contextlib import contextmanager

from ..config import DB


@contextmanager
def db():
    """Conexión que SIEMPRE se cierra."""
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()
