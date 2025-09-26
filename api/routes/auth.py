from flask import jsonify

from auth import login_required, require_user
from . import bp


@bp.get("/auth/debug")
def auth_debug():
    return jsonify({"message": "KeyN integration placeholder"})


@bp.get("/auth/me")
@login_required
def auth_me():
    user = require_user()
    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "display_name": user.display_name,
            "email": user.email,
            "onboarding_completed": user.onboarding_completed,
        }
    )
