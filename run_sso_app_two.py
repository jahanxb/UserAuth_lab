"""Run SSO Application Two on http://localhost:5002."""

import os

os.environ.setdefault("APP_NAME", "Library Portal")
os.environ.setdefault("APP_PORT", "5002")
os.environ.setdefault("KEYCLOAK_CLIENT_ID", "sso-app-two")
os.environ.setdefault("KEYCLOAK_CLIENT_SECRET", "app-two-secret")
os.environ.setdefault("SESSION_COOKIE_NAME", "sso_app_two_session")

from sso_app.app import app  # noqa: E402

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)
