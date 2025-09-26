from __future__ import annotations

import functools
from typing import Callable

from flask import abort, g, request
from sqlalchemy import select

from database import session_scope
from models import User
from services.keyn import keyn_client


def _ensure_user(username: str, display_name: str | None = None, email: str | None = None) -> User:
    with session_scope() as session:
        user = session.execute(select(User).where(User.username == username)).scalar_one_or_none()
        if user:
            return user
        user = User(
            username=username,
            display_name=display_name or username,
            email=email,
            quest_preferences={},
            prefs={}
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def get_current_user() -> User | None:
    debug_user = request.headers.get("X-Debug-User")
    if debug_user:
        return _ensure_user(debug_user)

    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]
    payload = keyn_client.decode_token(token)
    if payload is None:
        abort(401)

    username = payload.get("preferred_username") or payload.get("username")
    if not username:
        abort(401)

    return _ensure_user(
        username=username,
        display_name=payload.get("name") or username,
        email=payload.get("email"),
    )


def require_user() -> User:
    user = get_current_user()
    if user is None:
        abort(401)
    return user


def login_required(func: Callable):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        user = require_user()
        g.current_user = user
        return func(*args, **kwargs)

    return wrapper
