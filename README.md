# Python Authentication Labs

A complete teaching codebase for:

1. HTTP Basic Authentication
2. Opaque bearer-token authentication
3. JSON Web Token authentication
4. Server-side session authentication
5. OAuth 2.0 Authorization Code flow with PKCE
6. OpenID Connect login and Single Sign-On with Keycloak

## Demonstration accounts

### Core Flask application

| Username | Password | Role |
|---|---|---|
| `alice` | `alice123` | student |
| `admin` | `admin123` | admin |

### Keycloak realm

| Username | Password | Role |
|---|---|---|
| `alice` | `alice123` | student |
| `adminuser` | `admin123` | student, admin |

The passwords are intentionally simple for a controlled classroom environment. Do not reuse them elsewhere.

## 1. Create the Python environment

```bash
python -m venv .venv
```

Activate it:

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS or Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Optional environment file:

```bash
cp .env.example .env
```

On Windows, copy `.env.example` to `.env` using File Explorer or:

```powershell
Copy-Item .env.example .env
```

## 2. Run Basic, token, JWT, and session labs

```bash
python run_core.py
```

Open `http://localhost:5000`.

Import `postman/Authentication_Labs.postman_collection.json` into Postman.

## 3. Run Keycloak for OAuth and SSO

Docker Desktop must be running.

```bash
docker compose up -d
```

Wait until the Keycloak login page is available at `http://localhost:8080`.

Keycloak admin console:

- Username: `admin`
- Password: `admin`

The `auth-lab` realm, users, roles, and clients are imported automatically the first time the container starts.

## 4. Run the two SSO applications

Open two additional terminals with the virtual environment activated.

Terminal 1:

```bash
python run_sso_app_one.py
```

Terminal 2:

```bash
python run_sso_app_two.py
```

Open:

- University Portal: `http://localhost:5001`
- Library Portal: `http://localhost:5002`

Log into one application with `alice` / `alice123`. Then open the other application and click login. Keycloak should reuse the central login session.

## 5. OAuth in Postman

In Postman's OAuth 2.0 configuration, use:

- Grant type: Authorization Code with PKCE
- Callback URL: `https://oauth.pstmn.io/v1/callback`
- Authorization URL: `http://localhost:8080/realms/auth-lab/protocol/openid-connect/auth`
- Access Token URL: `http://localhost:8080/realms/auth-lab/protocol/openid-connect/token`
- Client ID: `postman-client`
- Client authentication: Send client credentials in body or no client secret (public client)
- Scope: `openid profile email`
- Code challenge method: `SHA-256`

## 6. Run automated tests

```bash
pytest -q
```

The tests cover Basic authentication, opaque-token issuance and revocation, JWT validation and role authorization, and session login/logout.

## Reset Keycloak

The realm is imported at startup. To recreate the container from the supplied realm file:

```bash
docker compose down
docker compose up -d
```

The current compose file does not attach a persistent data volume, so recreating the container returns it to the imported classroom configuration.

## Security scope

This project is intentionally designed for local education. Before production use, add TLS, a real database, secret management, CSRF protection for state-changing browser routes, rate limiting, audit logging, hardened cookie settings, secure key rotation, and deployment behind a production WSGI server.
