"""Reusable Flask OpenID Connect client used to demonstrate OAuth and SSO."""

from __future__ import annotations

import os

from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, session, url_for

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "SSO Application")
APP_PORT = int(os.getenv("APP_PORT", "5001"))
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "sso-app-one")
CLIENT_SECRET = os.getenv("KEYCLOAK_CLIENT_SECRET", "app-one-secret")
REALM = os.getenv("KEYCLOAK_REALM", "auth-lab")
KEYCLOAK_BASE_URL = os.getenv("KEYCLOAK_BASE_URL", "http://localhost:8080")
ISSUER_URL = f"{KEYCLOAK_BASE_URL}/realms/{REALM}"

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config.update(
    SECRET_KEY=os.getenv("FLASK_SECRET_KEY", f"development-secret-{CLIENT_ID}"),
    SESSION_COOKIE_NAME=os.getenv("SESSION_COOKIE_NAME", f"{CLIENT_ID}_session"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,  # Use True when deployed behind HTTPS.
)

oauth = OAuth(app)
keycloak = oauth.register(
    name="keycloak",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    server_metadata_url=f"{ISSUER_URL}/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid profile email",
        "code_challenge_method": "S256",
    },
)


@app.get("/")
def index():
    return render_template(
        "index.html",
        app_name=APP_NAME,
        client_id=CLIENT_ID,
        user=session.get("user"),
    )


@app.get("/login")
def login():
    redirect_uri = url_for("callback", _external=True)
    return keycloak.authorize_redirect(redirect_uri)


@app.get("/callback")
def callback():
    token = keycloak.authorize_access_token()
    userinfo = token.get("userinfo") or {}

    session["user"] = dict(userinfo)
    session["id_token"] = token.get("id_token")
    session["access_token_preview"] = (token.get("access_token") or "")[:32]
    return redirect(url_for("index"))


@app.post("/local-logout")
def local_logout():
    """End only this Flask application's local session."""
    session.clear()
    return redirect(url_for("index"))


@app.get("/sso-logout")
def sso_logout():
    """End the local session and request logout from Keycloak."""
    id_token = session.get("id_token")
    session.clear()
    return keycloak.logout_redirect(
        post_logout_redirect_uri=url_for("logged_out", _external=True),
        id_token_hint=id_token,
    )


@app.get("/logged-out")
def logged_out():
    # Authlib validates the provider logout response when state is returned.
    try:
        keycloak.validate_logout_response()
    except Exception:
        # Some provider configurations do not return state. The local lab can
        # still display a logged-out page because the local session is cleared.
        pass
    return render_template("logged_out.html", app_name=APP_NAME)


@app.get("/health")
def health():
    return {"status": "ok", "app_name": APP_NAME, "client_id": CLIENT_ID}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=APP_PORT, debug=True)
