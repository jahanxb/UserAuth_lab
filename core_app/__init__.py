"""Core Flask application for Basic, opaque-token, JWT, and session labs."""

from __future__ import annotations

import os
from pathlib import Path

from cachelib.file import FileSystemCache
from flask import Flask
from flask_session import Session

from .basic_auth import basic_bp
from .jwt_auth import jwt_bp
from .opaque_token_auth import opaque_bp
from .session_auth import session_bp


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config.from_mapping(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", "development-only-flask-secret"),
        SESSION_FILE_DIR=os.getenv("SESSION_FILE_DIR", ".flask_session"),
        SESSION_PERMANENT=False,
        SESSION_COOKIE_NAME="auth_lab_session",
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        # False is required for local HTTP. Set True behind HTTPS in production.
        SESSION_COOKIE_SECURE=False,
        JWT_SECRET_KEY=os.getenv(
            "JWT_SECRET_KEY",
            "development-only-jwt-secret-change-me-123456789",
        ),
        JWT_ISSUER=os.getenv("JWT_ISSUER", "python-authentication-lab"),
        JWT_AUDIENCE=os.getenv("JWT_AUDIENCE", "lab-api"),
        JWT_EXPIRATION_SECONDS=int(os.getenv("JWT_EXPIRATION_SECONDS", "300")),
        OPAQUE_TOKEN_EXPIRATION_SECONDS=int(
            os.getenv("OPAQUE_TOKEN_EXPIRATION_SECONDS", "900")
        ),
    )

    if test_config:
        app.config.update(test_config)

    session_dir = Path(app.config["SESSION_FILE_DIR"]).resolve()
    session_dir.mkdir(parents=True, exist_ok=True)
    app.config["SESSION_TYPE"] = "cachelib"
    app.config["SESSION_CACHELIB"] = FileSystemCache(
        cache_dir=str(session_dir), threshold=500, default_timeout=3600
    )

    Session(app)

    app.register_blueprint(basic_bp)
    app.register_blueprint(opaque_bp)
    app.register_blueprint(jwt_bp)
    app.register_blueprint(session_bp)

    @app.get("/")
    def index():
        from flask import render_template

        return render_template("index.html")

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "core-authentication-lab"}

    return app
