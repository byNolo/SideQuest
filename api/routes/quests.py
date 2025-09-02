from . import bp
from flask import jsonify
from datetime import date

@bp.get("/quests/today")
def todays_quest():
    # TODO: generate per-user using templates, weather + OSM
    return jsonify({
        "date": date.today().isoformat(),
        "title": "Neighborhood Snapshot",
        "details": "Find a park, library, or cafe within ~1km and include something yellow in frame.",
        "difficulty": 2,
        "modifiers": ["yellow","rule_of_thirds"],
    })
