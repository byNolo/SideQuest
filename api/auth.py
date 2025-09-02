import os, jwt, requests
from flask import request, abort
from config import Config

# Minimal token passthrough; replace with JWKS verify using Config.KEYN_JWKS_URL

def require_user():
    # For local dev, allow X-Debug-User header
    debug_user = request.headers.get("X-Debug-User")
    if debug_user:
        return {"id": 1, "username": debug_user}
    auth = request.headers.get("Authorization","")
    if not auth.startswith("Bearer "):
        abort(401)
    token = auth.split(" ",1)[1]
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return {"id": payload.get("sub"), "username": payload.get("preferred_username","user")}
    except Exception:
        abort(401)
