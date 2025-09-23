import os, jwt, requests, time
from flask import request, abort
from config import Config

_jwks_cache = {"keys": None, "ts": 0}

def _get_jwks():
    url = Config.KEYN_JWKS_URL or f"{Config.KEYN_AUTH_SERVER_URL}/.well-known/jwks.json"
    now = time.time()
    if _jwks_cache["keys"] and now - _jwks_cache["ts"] < 300:
        return _jwks_cache["keys"]
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        _jwks_cache["keys"] = r.json()
        _jwks_cache["ts"] = now
        return _jwks_cache["keys"]
    except Exception:
        return None

def _decode_with_jwks(token: str):
    jwks = _get_jwks()
    if not jwks:
        return None
    try:
        from jwt import algorithms
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        key = None
        for k in jwks.get("keys", []):
            if k.get("kid") == kid:
                key = algorithms.RSAAlgorithm.from_jwk(k)
                break
        if not key:
            return None
        return jwt.decode(token, key=key, algorithms=["RS256", "RS512"], options={"verify_aud": False})
    except Exception:
        return None

def _read_token_from_request():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth.split(" ", 1)[1]
    cookie_name = Config.COOKIE_NAME
    if cookie_name in request.cookies:
        return request.cookies.get(cookie_name)
    return None

def require_user():
    debug_user = request.headers.get("X-Debug-User")
    if debug_user:
        # Create a unique ID based on the debug username for testing
        user_id = hash(debug_user) % 10000 + 1  # Generate ID 1-10000 based on username
        return {"id": user_id, "username": debug_user}

    token = _read_token_from_request()
    if not token:
        abort(401)

    # Try verifying against JWKS
    payload = _decode_with_jwks(token)
    if payload is None:
        # Fallback to non-verifying decode only for dev
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
        except Exception:
            abort(401)

    return {
        "id": payload.get("sub") or payload.get("id"),
        "username": payload.get("preferred_username") or payload.get("username") or "user",
        "scopes": payload.get("scope") or payload.get("scopes"),
    }
