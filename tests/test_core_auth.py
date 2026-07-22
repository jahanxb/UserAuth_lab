from __future__ import annotations

import base64


def test_basic_auth_success(client):
    credentials = base64.b64encode(b"alice:alice123").decode()
    response = client.get(
        "/basic/profile", headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 200
    assert response.get_json()["user"]["username"] == "alice"


def test_basic_auth_rejects_bad_password(client):
    credentials = base64.b64encode(b"alice:wrong").decode()
    response = client.get(
        "/basic/profile", headers={"Authorization": f"Basic {credentials}"}
    )
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_opaque_token_login_profile_and_revocation(client):
    login = client.post(
        "/token/login", json={"username": "alice", "password": "alice123"}
    )
    token = login.get_json()["access_token"]

    profile = client.get(
        "/token/profile", headers={"Authorization": f"Bearer {token}"}
    )
    assert profile.status_code == 200
    assert profile.get_json()["server_lookup_required"] is True

    logout = client.post(
        "/token/logout", headers={"Authorization": f"Bearer {token}"}
    )
    assert logout.status_code == 200

    reused = client.get(
        "/token/profile", headers={"Authorization": f"Bearer {token}"}
    )
    assert reused.status_code == 401


def test_jwt_profile_and_role_authorization(client):
    login = client.post(
        "/jwt/login", json={"username": "alice", "password": "alice123"}
    )
    token = login.get_json()["access_token"]

    profile = client.get(
        "/jwt/profile", headers={"Authorization": f"Bearer {token}"}
    )
    assert profile.status_code == 200
    assert profile.get_json()["claims"]["sub"] == "alice"

    forbidden = client.get(
        "/jwt/admin", headers={"Authorization": f"Bearer {token}"}
    )
    assert forbidden.status_code == 403

    admin_login = client.post(
        "/jwt/login", json={"username": "admin", "password": "admin123"}
    )
    admin_token = admin_login.get_json()["access_token"]
    allowed = client.get(
        "/jwt/admin", headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert allowed.status_code == 200


def test_session_login_and_logout(client):
    login = client.post(
        "/session/login",
        json={"username": "alice", "password": "alice123"},
    )
    assert login.status_code == 200

    profile = client.get("/session/profile", headers={"Accept": "application/json"})
    assert profile.status_code == 200
    assert profile.get_json()["user"]["username"] == "alice"

    logout = client.post(
        "/session/logout",
        headers={"Accept": "application/json", "Content-Type": "application/json"},
        json={},
    )
    assert logout.status_code == 200

    after = client.get("/session/profile", headers={"Accept": "application/json"})
    assert after.status_code == 401
