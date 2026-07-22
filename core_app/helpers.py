"""Shared parsing and response helpers."""

from __future__ import annotations

from flask import Response, jsonify, request


def json_error(message: str, status_code: int, **extra) -> tuple[Response, int]:
    payload = {"error": message}
    payload.update(extra)
    return jsonify(payload), status_code


def bearer_token_from_request() -> str | None:
    authorization = request.headers.get("Authorization", "")
    scheme, separator, value = authorization.partition(" ")
    if not separator or scheme.lower() != "bearer" or not value.strip():
        return None
    return value.strip()
