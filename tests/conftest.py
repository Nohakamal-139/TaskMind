import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import get_connection, init_db  # noqa: E402


@pytest.fixture
def conn():
    """A fresh empty in-memory database for every test."""
    c = get_connection(":memory:")
    init_db(c)
    yield c
    c.close()
