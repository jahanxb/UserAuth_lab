"""JSON Web Token authentication lab routes."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from flask import Blueprint, current_app, jsonify, request

from .helpers import bearer_token_from_request, json_error
from .users import authenticate, public_user

jwt_bp = Blueprint("jwt", __name__, url_prefix="/jwt")


def _issue_token(username: str, role: str) -> tuple[str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        seconds=current_app.config["JWT_EXPIRATION_SECONDS"]
    )
    payload = {
        "sub": username,
        "role": role,
        "iss": current_app.config["JWT_ISSUER"],
        "aud": current_app.config["JWT_AUDIENCE"],
        "iat": now,
        "nbf": now,
        "exp": expires_at,
    }
    token = jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
        headers={"typ": "JWT"},
    )
    return token, expires_at


def _decode_request_token() -> tuple[dict | None, tuple | None]:
    token = bearer_token_from_request()
    if token is None:
        return None, json_error("A JWT Bearer token is required", 401)

    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"],
            issuer=current_app.config["JWT_ISSUER"],
            audience=current_app.config["JWT_AUDIENCE"],
            options={"require": ["sub", "role", "iss", "aud", "iat", "exp"]},
        )
    except jwt.ExpiredSignatureError:
        return None, json_error("The JWT has expired", 401)
    except jwt.ImmatureSignatureError:
        return None, json_error("The JWT is not valid yet", 401)
    except jwt.InvalidAudienceError:
        return None, json_error("The JWT audience is invalid", 401)
    except jwt.InvalidIssuerError:
        return None, json_error("The JWT issuer is invalid", 401)
    except jwt.InvalidTokenError as exc:
        return None, json_error("The JWT is invalid", 401, detail=str(exc))

    return payload, None


@jwt_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    user = authenticate(data.get("username"), data.get("password"))
    if user is None:
        return json_error("Invalid username or password", 401)

    token, expires_at = _issue_token(user.username, user.role)
    return jsonify(
        {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": current_app.config["JWT_EXPIRATION_SECONDS"],
            "expires_at": expires_at.isoformat(),
        }
    )


@jwt_bp.get("/profile")
def profile():
    payload, error = _decode_request_token()
    if error:
        return error

    return jsonify(
        {
            "message": "JWT authentication succeeded",
            "authentication_method": "JSON Web Token",
            "claims": payload,
            "server_token_lookup_required": False,
        }
    )


@jwt_bp.get("/admin")
def admin_only():
    payload, error = _decode_request_token()
    if error:
        return error

    if payload["role"] != "admin":
        return json_error(
            "Authentication succeeded, but the user lacks the admin role", 403
        )

    return jsonify(
        {
            "message": "Administrator authorization succeeded",
            "subject": payload["sub"],
            "role": payload["role"],
        }
    )
