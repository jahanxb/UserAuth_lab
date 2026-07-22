"""Server-side session authentication lab routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from .helpers import json_error
from .users import USERS, authenticate, public_user

session_bp = Blueprint("session_auth", __name__, url_prefix="/session")


@session_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("session_login.html", error=None)

    if request.is_json:
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")
    else:
        username = request.form.get("username")
        password = request.form.get("password")

    user = authenticate(username, password)
    if user is None:
        if request.is_json:
            return json_error("Invalid username or password", 401)
        return render_template(
            "session_login.html", error="Invalid username or password"
        ), 401

    # Defend against session fixation by clearing any previous session data.
    session.clear()
    session["username"] = user.username
    session["role"] = user.role

    if request.is_json:
        return jsonify(
            {
                "message": "Server-side session created",
                "user": public_user(user),
            }
        )
    return redirect(url_for("session_auth.profile"))


@session_bp.get("/profile")
def profile():
    username = session.get("username")
    if username is None or username not in USERS:
        if request.accept_mimetypes.best == "application/json":
            return json_error("No authenticated session exists", 401)
        return redirect(url_for("session_auth.login"))

    user = USERS[username]
    if request.accept_mimetypes.best == "application/json":
        return jsonify(
            {
                "message": "Session authentication succeeded",
                "authentication_method": "Server-side session",
                "user": public_user(user),
                "browser_holds": "A session identifier cookie",
                "server_holds": "The authenticated session state",
            }
        )

    return render_template("session_profile.html", user=user)


@session_bp.post("/logout")
def logout():
    session.clear()
    if request.is_json or request.accept_mimetypes.best == "application/json":
        return jsonify({"message": "Session ended"})
    return redirect(url_for("session_auth.login"))
