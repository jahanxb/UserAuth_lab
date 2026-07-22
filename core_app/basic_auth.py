"""HTTP Basic Authentication lab routes."""

from __future__ import annotations

import base64
import binascii

from flask import Blueprint, jsonify, request

from .helpers import json_error
from .users import authenticate, public_user

basic_bp = Blueprint("basic", __name__, url_prefix="/basic")


def _unauthorized(message: str):
    response, status = json_error(message, 401)
    response.headers["WWW-Authenticate"] = 'Basic realm="Python Authentication Lab"'
    return response, status


@basic_bp.get("/profile")
def profile():
    authorization = request.headers.get("Authorization", "")
    scheme, separator, encoded = authorization.partition(" ")
    
    print(   "scheme: " ,scheme, "| separator: ", separator, "| encoded: ", encoded )

    if not separator or scheme.lower() != "basic" or not encoded:
        return _unauthorized("Basic credentials are required")

    try:
        decoded = base64.b64decode(encoded, validate=True).decode("utf-8")
        username, password = decoded.split(":", 1)
        
        print("Username: ",username , "| Password: ",password)
    except (binascii.Error, UnicodeDecodeError, ValueError):
        return _unauthorized("The Basic Authorization header is malformed")

    user = authenticate(username, password)
    if user is None:
        return _unauthorized("Invalid username or password")

    return jsonify(
        {
            "message": "Basic authentication succeeded",
            "authentication_method": "HTTP Basic",
            "user": public_user(user),
            "observation": "The username and password were supplied on this request.",
        }
    )
