import os

# Use an in-memory SQLite database for the whole test session (shared via the
# StaticPool configured in app.database). Must be set before importing the app.
os.environ["DATABASE_URL"] = "sqlite://"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)
