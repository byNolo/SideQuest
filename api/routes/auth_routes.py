from . import bp
from flask import jsonify, request, redirect, make_response
from config import Config
import secrets
from urllib.parse import urlencode
import requests
from database import SessionLocal
from sqlalchemy import select
from models import User


def _cookie_args():
    return {
        "secure": Config.COOKIE_SECURE,
        "httponly": True,
        "samesite": Config.COOKIE_SAMESITE,
        "path": "/",
        "max_age": 3600,  # 1 hour, matches typical access token lifetime
    }


def _build_redirect_uri():
    return f"{Config.PUBLIC_URL}/api/auth/callback"


def _build_authorize_url(scopes: list[str], state: str) -> str:
    params = {
        "client_id": Config.KEYN_CLIENT_ID,
        "redirect_uri": _build_redirect_uri(),
        "scope": ",".join(scopes),
        "state": state,
    }
    return f"{Config.KEYN_AUTH_SERVER_URL}/oauth/authorize?{urlencode(params)}"


@bp.get("/auth/login-url")
def auth_login_url():
    if not Config.KEYN_CLIENT_ID or not Config.KEYN_CLIENT_SECRET:
        return jsonify({
            "error": "config_error",
            "message": "Missing KEYN_CLIENT_ID/KEYN_CLIENT_SECRET in environment",
        }), 500

    scopes_param = request.args.get("scopes")
    scopes = (
        [s.strip() for s in scopes_param.split(",") if s.strip()] if scopes_param else
        ["id", "username", "email", "full_name", "display_name", "created_at", "is_verified"]
    )
    state = secrets.token_urlsafe(24)

    url = _build_authorize_url(scopes, state)

    resp = jsonify({"url": url})
    # store state in a short-lived cookie for CSRF protection
    resp.set_cookie("sq_oauth_state", state, max_age=600, secure=Config.COOKIE_SECURE, httponly=True, samesite=Config.COOKIE_SAMESITE, path="/")
    return resp


@bp.get("/auth/login")
def auth_login_redirect():
    # Convenience endpoint to perform a 302 redirect to KeyN
    state = secrets.token_urlsafe(24)
    scopes = ["id", "username", "email", "full_name", "display_name", "created_at", "is_verified"]
    url = _build_authorize_url(scopes, state)
    resp = redirect(url, code=302)
    resp.set_cookie("sq_oauth_state", state, max_age=600, secure=Config.COOKIE_SECURE, httponly=True, samesite=Config.COOKIE_SAMESITE, path="/")
    return resp


@bp.get("/auth/callback")
def auth_callback():
    error = request.args.get("error")
    if error:
        return jsonify({"error": error, "error_description": request.args.get("error_description")}), 400

    state = request.args.get("state")
    code = request.args.get("code")
    if not state or not code:
        return jsonify({"error": "invalid_request"}), 400

    cookie_state = request.cookies.get("sq_oauth_state")
    if not cookie_state or cookie_state != state:
        return jsonify({"error": "invalid_state"}), 400

    token_url = f"{Config.KEYN_AUTH_SERVER_URL}/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": Config.KEYN_CLIENT_ID,
        "client_secret": Config.KEYN_CLIENT_SECRET,
        "redirect_uri": _build_redirect_uri(),
    }
    try:
        tr = requests.post(token_url, data=data, timeout=10)
        if tr.status_code != 200:
            return jsonify({"error": "token_exchange_failed", "details": tr.text}), 400
        token = tr.json().get("access_token")
        if not token:
            return jsonify({"error": "no_access_token"}), 400
    except requests.RequestException as e:
        return jsonify({"error": "network_error", "details": str(e)}), 502

    # Fetch user info and upsert into local DB
    try:
        ur = requests.get(
            f"{Config.KEYN_AUTH_SERVER_URL}/api/user-scoped",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if ur.status_code == 200:
            u = ur.json()
            username = u.get("username")
            if username:
                with SessionLocal() as db:
                    existing = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
                    if existing:
                        # Update select fields if provided
                        if u.get("display_name") is not None:
                            existing.display_name = u.get("display_name")
                        if u.get("email") is not None:
                            existing.email = u.get("email")
                    else:
                        new_user = User(
                            username=username,
                            display_name=u.get("display_name"),
                            email=u.get("email"),
                        )
                        db.add(new_user)
                    db.commit()
    except requests.RequestException:
        pass

    # Set httpOnly cookie with access token, then redirect to SPA root
    resp = make_response(redirect("/", code=302))
    args = _cookie_args()
    resp.set_cookie(Config.COOKIE_NAME, token, **args)
    # clear state cookie
    resp.delete_cookie("sq_oauth_state", path="/")
    return resp


@bp.get("/auth/me")
def auth_me():
    token = request.cookies.get(Config.COOKIE_NAME)
    if not token:
        return jsonify({"authenticated": False})
    try:
        ur = requests.get(
            f"{Config.KEYN_AUTH_SERVER_URL}/api/user-scoped",
            headers={"Authorization": f"Bearer {token}"},
            timeout=5,
        )
        if ur.status_code == 200:
            data = ur.json()
            return jsonify({"authenticated": True, "user": data})
        else:
            # token invalid/expired
            resp = jsonify({"authenticated": False})
            resp.delete_cookie(Config.COOKIE_NAME, path="/")
            return resp, 401
    except requests.RequestException:
        return jsonify({"error": "keyn_unavailable"}), 502


@bp.post("/auth/logout")
def auth_logout():
    resp = jsonify({"ok": True})
    resp.delete_cookie(Config.COOKIE_NAME, path="/")
    return resp
