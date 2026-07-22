"""Run SSO Application One on http://localhost:5001."""

import os

os.environ.setdefault("APP_NAME", "University Portal")
os.environ.setdefault("APP_PORT", "5001")
os.environ.setdefault("KEYCLOAK_CLIENT_ID", "sso-app-one")
os.environ.setdefault("KEYCLOAK_CLIENT_SECRET", "app-one-secret")
os.environ.setdefault("SESSION_COOKIE_NAME", "sso_app_one_session")

from sso_app.app import app  # noqa: E402

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
