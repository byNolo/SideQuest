from datetime import date

from flask import jsonify

from auth import login_required, require_user
from . import bp


def _quest_title(preferences: dict | None) -> str:
    categories = (preferences or {}).get("categories") or []
    if "art" in categories:
        return "Street Sketch Study"
    if "social" in categories:
        return "Neighborhood High-Five"
    if "outdoor" in categories:
        return "Sunlit Explorer"
    return "Neighborhood Snapshot"


@bp.get("/quests/today")
@login_required
def todays_quest():
    user = require_user()

    location_label = user.default_location_name or "your neighborhood"
    title = _quest_title(user.quest_preferences)

    description = (
        "Grab your camera (or phone) and capture a detail that makes "
        f"{location_label} feel unique today."
    )
    if title == "Street Sketch Study":
        description = (
            f"Take a quick pencil or digital sketch inspired by something in {location_label}. "
            "Focus on shapes and textures—perfection not required!"
        )
    elif title == "Neighborhood High-Five":
        description = (
            f"Offer a compliment, high-five, or kind note to someone in {location_label} and record "
            "what happened."
        )
    elif title == "Sunlit Explorer":
        description = (
            f"Head outside within {user.location_radius_km or 2:.0f} km of {location_label} and capture a "
            "photo of how the light hits your surroundings."
        )

    quest_payload = {
        "date": date.today().isoformat(),
        "title": title,
        "description": description,
        "hints": [
            "Spend at least 10 minutes observing before documenting.",
            "Share one surprising detail with your future self.",
        ],
        "location": {
            "name": user.default_location_name,
            "lat": user.default_lat,
            "lon": user.default_lon,
            "radius_km": user.location_radius_km,
        }
        if user.default_lat is not None and user.default_lon is not None
        else None,
        "personalization": {
            "preferences": user.quest_preferences or {},
            "privacy": user.privacy,
        },
    }

    return jsonify({"quest": quest_payload})
