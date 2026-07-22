"""Small in-memory user repository used only for classroom demonstrations."""

from __future__ import annotations

from dataclasses import dataclass

from werkzeug.security import check_password_hash, generate_password_hash


@dataclass(frozen=True)
class User:
    username: str
    password_hash: str
    role: str
    display_name: str


# Passwords are intentionally simple for a controlled classroom lab.
# Never use these passwords in a real system.
USERS: dict[str, User] = {
    "alice": User(
        username="alice",
        password_hash=generate_password_hash("alice123"),
        role="student",
        display_name="Alice Student",
    ),
    "admin": User(
        username="admin",
        password_hash=generate_password_hash("admin123"),
        role="admin",
        display_name="Admin User",
    ),
}


def authenticate(username: str | None, password: str | None) -> User | None:
    """Return the matching user when the supplied credentials are valid."""
    if not username or password is None:
        return None

    user = USERS.get(username)
    if user is None or not check_password_hash(user.password_hash, password):
        return None
    return user


def public_user(user: User) -> dict[str, str]:
    return {
        "username": user.username,
        "display_name": user.display_name,
        "role": user.role,
    }
