
- (1) Authentication versus authorization
- (2): Basic Authentication
- (3): Opaque bearer token
- (4): JWT
- (5): Server-side session
- (6): OAuth Authorization Code with PKCE
- (7): SSO using the two Flask clients
- Comparison and security recap

## Before class

1. Install Python, Docker Desktop, Postman, and VS Code.
2. Run `python -m pip install -r requirements.txt`.
3. Run `pytest -q`.
4. Start Keycloak and verify realm import.
5. Start all three Flask processes.
6. Import the Postman collection.
7. Clear browser cookies or use a fresh browser profile before the SSO demonstration.

## Key observations to elicit

- Basic sends reusable credentials on each request.
- Opaque tokens require server-side lookup and are easy to revoke.
- JWTs carry signed claims and can be verified locally, but early revocation requires additional design.
- Session cookies are sent automatically by browsers, so CSRF matters.
- OAuth delegates limited access; it is not itself a user authentication protocol.
- OpenID Connect adds identity and an ID Token on top of OAuth.
- SSO means applications trust the same identity provider; it does not mean the applications share one local session cookie.
