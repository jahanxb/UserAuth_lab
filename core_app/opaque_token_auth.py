"""Opaque bearer token authentication lab routes."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, request

from .helpers import bearer_token_from_request, json_error
from .users import USERS, authenticate, public_user

opaque_bp = Blueprint("opaque", __name__, url_prefix="/token")


@dataclass
class TokenRecord:
    username: str
    expires_at: datetime


# A production implementation would use a database, cache, or authorization server.
ACTIVE_TOKENS: dict[str, TokenRecord] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _find_valid_record(token: str) -> TokenRecord | None:
    record = ACTIVE_TOKENS.get(token)
    if record is None:
        return None
    if record.expires_at <= _now():
        ACTIVE_TOKENS.pop(token, None)
        return None
    return record


@opaque_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = authenticate(data.get("username"), data.get("password"))
    if user is None:
        return json_error("Invalid username or password", 401)

    lifetime = current_app.config["OPAQUE_TOKEN_EXPIRATION_SECONDS"]
    token = secrets.token_urlsafe(32)
    expires_at = _now() + timedelta(seconds=lifetime)
    ACTIVE_TOKENS[token] = TokenRecord(user.username, expires_at)

    return jsonify(
        {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": lifetime,
            "expires_at": expires_at.isoformat(),
        }
    )


@opaque_bp.get("/profile")
def profile():
    token = bearer_token_from_request()
    if token is None:
        return json_error("A Bearer token is required", 401)

    record = _find_valid_record(token)
    if record is None:
        return json_error("The token is invalid, expired, or revoked", 401)

    return jsonify(
        {
            "message": "Opaque token authentication succeeded",
            "authentication_method": "Opaque bearer token",
            "user": public_user(USERS[record.username]),
            "server_lookup_required": True,
        }
    )


@opaque_bp.post("/logout")
def logout():
    token = bearer_token_from_request()
    if token is None:
        return json_error("A Bearer token is required", 401)

    existed = ACTIVE_TOKENS.pop(token, None) is not None
    return jsonify(
        {
            "message": "Token revoked" if existed else "Token was already invalid",
            "revoked": existed,
        }
    )


@opaque_bp.post("/introspect")
def introspect():
    """Educational endpoint showing the server-side lookup performed for opaque tokens."""
    data = request.get_json(silent=True) or {}
    token = data.get("token", "")
    record = _find_valid_record(token)
    if record is None:
        return jsonify({"active": False})

    return jsonify(
        {
            "active": True,
            "username": record.username,
            "expires_at": record.expires_at.isoformat(),
        }
    )
