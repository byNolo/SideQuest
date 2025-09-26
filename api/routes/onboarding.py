from __future__ import annotations

from typing import Any

import requests
from flask import jsonify, request
from sqlalchemy import select

from auth import login_required, require_user
from database import session_scope
from models import Location, User
from . import bp


def _serialize_user(user: User) -> dict[str, Any]:
    return {
        "id": user.id,
        "username": user.username,
        "display_name": user.display_name,
        "email": user.email,
    "bio": user.bio,
    "avatar_url": user.avatar_url,
    "privacy": user.privacy,
    "prefs": user.prefs or {},
    "quest_preferences": user.quest_preferences or {},
        "location": {
            "lat": user.default_lat,
            "lon": user.default_lon,
            "name": user.default_location_name,
            "radius_km": user.location_radius_km,
        }
        if user.default_lat is not None and user.default_lon is not None
        else None,
        "onboarding": {
            "completed": user.onboarding_completed,
            "step": user.onboarding_step,
        },
        "webpush_registered": user.webpush_endpoint is not None,
        "created_at": user.created_at.isoformat(),
    }


@bp.get("/me")
@login_required
def get_me():
    user = require_user()
    return jsonify(_serialize_user(user))


@bp.patch("/me/preferences")
@login_required
def update_preferences():
    user = require_user()
    payload = request.get_json(silent=True) or {}

    quest_prefs = payload.get("quest_preferences")
    prefs = payload.get("prefs")
    bio = payload.get("bio")
    display_name = payload.get("display_name")
    privacy = payload.get("privacy")

    with session_scope() as session:
        db_user = session.get(User, user.id)
        if db_user is None:
            return jsonify({"error": "User not found"}), 404

        if isinstance(quest_prefs, dict):
            db_user.quest_preferences = {**(db_user.quest_preferences or {}), **quest_prefs}
        if isinstance(prefs, dict):
            db_user.prefs = {**(db_user.prefs or {}), **prefs}
        if isinstance(bio, str):
            db_user.bio = bio
        if isinstance(display_name, str):
            db_user.display_name = display_name
        if privacy in {"public", "friends_only"}:
            db_user.privacy = privacy

        session.add(db_user)

    return jsonify({"ok": True})


@bp.post("/me/location")
@login_required
def update_location():
    user = require_user()
    payload = request.get_json(silent=True) or {}

    try:
        lat = float(payload["lat"])
        lon = float(payload["lon"])
    except (KeyError, TypeError, ValueError):
        return jsonify({"error": "lat and lon are required"}), 400

    label = payload.get("name") or payload.get("label")
    radius_raw = payload.get("radius_km")
    try:
        radius_km = float(radius_raw) if radius_raw is not None else None
    except (TypeError, ValueError):
        radius_km = None

    precision = payload.get("precision_m")
    try:
        precision_m = float(precision) if precision is not None else None
    except (TypeError, ValueError):
        precision_m = None

    source = payload.get("source", "manual")

    with session_scope() as session:
        db_user = session.get(User, user.id)
        if db_user is None:
            return jsonify({"error": "User not found"}), 404

        db_user.default_lat = lat
        db_user.default_lon = lon
        if radius_km is not None:
            db_user.location_radius_km = radius_km
        elif db_user.location_radius_km is None:
            db_user.location_radius_km = 2.0
        db_user.default_location_name = label
        db_user.locations.append(
            Location(
                lat=lat,
                lon=lon,
                name=label,
                source=source,
                precision_m=precision_m,
                user_id=user.id,
            )
        )
        session.add(db_user)

    return jsonify({"ok": True})


@bp.post("/me/notifications/register")
@login_required
def register_notifications():
    user = require_user()
    payload = request.get_json(silent=True) or {}

    endpoint = payload.get("endpoint")
    keys = payload.get("keys")

    if not isinstance(endpoint, str) or not endpoint.strip():
        return jsonify({"error": "endpoint is required"}), 400

    with session_scope() as session:
        db_user = session.get(User, user.id)
        if db_user is None:
            return jsonify({"error": "User not found"}), 404

        db_user.webpush_endpoint = endpoint.strip()
        db_user.webpush_keys = keys if isinstance(keys, dict) else None
        session.add(db_user)

    return jsonify({"ok": True})


@bp.delete("/me/notifications/register")
@login_required
def unregister_notifications():
    user = require_user()

    with session_scope() as session:
        db_user = session.get(User, user.id)
        if db_user is None:
            return jsonify({"error": "User not found"}), 404

        db_user.webpush_endpoint = None
        db_user.webpush_keys = None
        session.add(db_user)

    return jsonify({"ok": True})


@bp.post("/me/onboarding/complete-step")
@login_required
def complete_step():
    user = require_user()
    payload = request.get_json(silent=True) or {}
    step = payload.get("step")
    if step not in {"location", "preferences", "notifications", "complete"}:
        return jsonify({"error": "invalid step"}), 400

    with session_scope() as session:
        db_user = session.get(User, user.id)
        if db_user is None:
            return jsonify({"error": "User not found"}), 404

        db_user.onboarding_step = step
        if step == "complete":
            db_user.onboarding_completed = True
        session.add(db_user)

    return jsonify({"ok": True, "step": step})


@bp.get("/me/onboarding/status")
@login_required
def onboarding_status():
    user = require_user()

    location_done = user.default_lat is not None and user.default_lon is not None
    preferences_done = bool(user.quest_preferences)
    notifications_done = bool(user.webpush_endpoint)
    completion_done = bool(user.onboarding_completed)

    steps_meta = [
        {
            "id": "location",
            "label": "Set your home base",
            "description": "Pick where quests should start and how far you're willing to travel.",
            "completed": location_done,
        },
        {
            "id": "preferences",
            "label": "Tell us what you like",
            "description": "Choose quest styles so we can tailor the daily challenge.",
            "completed": preferences_done,
        },
        {
            "id": "notifications",
            "label": "Stay in the loop",
            "description": "Enable browser notifications so you never miss a quest drop.",
            "completed": notifications_done,
        },
        {
            "id": "complete",
            "label": "You're ready to quest",
            "description": "Review your info and dive into your first adventure.",
            "completed": completion_done,
        },
    ]

    explicit_step = user.onboarding_step
    current_step = None
    for step in steps_meta:
        if not step["completed"]:
            current_step = step["id"]
            break

    if explicit_step and any(step["id"] == explicit_step for step in steps_meta):
        current_step = explicit_step
    if completion_done:
        current_step = "complete"

    next_step = None
    for step in steps_meta:
        if not step["completed"]:
            next_step = step["id"]
            break

    profile_snapshot = {
        "display_name": user.display_name,
        "username": user.username,
        "location": {
            "name": user.default_location_name,
            "lat": user.default_lat,
            "lon": user.default_lon,
            "radius_km": user.location_radius_km,
        }
        if location_done
        else None,
        "quest_preferences": user.quest_preferences or {},
        "notifications": {
            "webpush_registered": bool(user.webpush_endpoint),
        },
    }

    return jsonify(
        {
            "completed": completion_done,
            "current_step": current_step,
            "next_step": None if completion_done else next_step,
            "steps_completed": [step["id"] for step in steps_meta if step["completed"]],
            "total_steps": len(steps_meta),
            "steps": steps_meta,
            "profile": profile_snapshot,
        }
    )


@bp.get("/geocode")
@login_required
def geocode():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "q parameter required"}), 400

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "json", "limit": 5, "addressdetails": 1},
            headers={"User-Agent": "SideQuest/1.0"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return jsonify({"error": f"lookup_failed: {exc}"}), 502

    results = []
    for item in response.json():
        results.append(
            {
                "display_name": item.get("display_name"),
                "lat": float(item.get("lat")),
                "lon": float(item.get("lon")),
                "type": item.get("type"),
                "importance": item.get("importance"),
                "address": item.get("address", {}),
            }
        )
    return jsonify({"locations": results})


@bp.get("/geocode/reverse")
@login_required
def reverse_geocode():
    lat_raw = request.args.get("lat")
    lon_raw = request.args.get("lon")

    try:
        lat = float(lat_raw)
        lon = float(lon_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "lat and lon are required"}), 400

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "lat": lat,
                "lon": lon,
                "format": "jsonv2",
                "addressdetails": 1,
            },
            headers={"User-Agent": "SideQuest/1.0"},
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return jsonify({"error": f"lookup_failed: {exc}"}), 502

    data = response.json() or {}

    result = {
        "display_name": data.get("display_name"),
        "lat": lat,
        "lon": lon,
        "address": data.get("address", {}),
    }

    return jsonify({"location": result})
