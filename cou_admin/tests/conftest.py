import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Fixture to initialize the test client."""
    return TestClient(app)
