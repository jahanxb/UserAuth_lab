from __future__ import annotations

import pytest

from core_app import create_app
from core_app.opaque_token_auth import ACTIVE_TOKENS


@pytest.fixture()
def app(tmp_path):
    ACTIVE_TOKENS.clear()
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-flask-secret",
            "SESSION_FILE_DIR": str(tmp_path / "sessions"),
            "JWT_SECRET_KEY": "test-jwt-secret-that-is-at-least-32-bytes-long",
            "JWT_EXPIRATION_SECONDS": 300,
            "OPAQUE_TOKEN_EXPIRATION_SECONDS": 300,
        }
    )
    yield app
    ACTIVE_TOKENS.clear()


@pytest.fixture()
def client(app):
    return app.test_client()
