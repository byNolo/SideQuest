from . import bp
from flask import jsonify, request
from datetime import date
from auth import require_user
from quest_service import quest_generator
from database import SessionLocal
from sqlalchemy import select
from models import QuestTemplate

@bp.get("/quests/today")
def todays_quest():
    """Get or generate today's quest for the current user"""
    try:
        user = require_user()
        user_id = user["id"]
        
        quest_data = quest_generator.generate_quest_for_user(user_id, date.today())
        
        if quest_data:
            return jsonify(quest_data)
        else:
            return jsonify({"error": "Could not generate quest"}), 500
            
    except Exception as e:
        # If authentication fails, return a generic quest for demo purposes
        return jsonify({
            "date": date.today().isoformat(),
            "title": "Neighborhood Snapshot",
            "details": "Find a park, library, or cafe within ~1km and include something yellow in frame.",
            "difficulty": 2,
            "modifiers": ["yellow", "rule_of_thirds"],
            "note": "Login to get personalized quests!"
        })

@bp.get("/quests/history")
def quest_history():
    """Get quest history for the current user"""
    user = require_user()
    # TODO: Implement quest history
    return jsonify({"quests": [], "message": "Quest history coming soon"})

@bp.post("/quests/generate")  
def generate_quest():
    """Admin/test endpoint to generate quests"""
    user = require_user()
    # TODO: Add admin check
    
    target_date = request.json.get("date") if request.json else None
    if target_date:
        target_date = date.fromisoformat(target_date)
    else:
        target_date = date.today()
    
    quest_data = quest_generator.generate_quest_for_user(user["id"], target_date)
    
    if quest_data:
        return jsonify(quest_data)
    else:
        return jsonify({"error": "Could not generate quest"}), 500

@bp.get("/templates")
def list_templates():
    """Get list of all quest templates"""
    with SessionLocal() as db:
        templates = db.execute(
            select(QuestTemplate).where(QuestTemplate.enabled == True)
        ).scalars().all()
        
        return jsonify({
            "templates": [
                {
                    "id": t.id,
                    "title": t.title,
                    "body_template": t.body_template,
                    "tags": t.tags,
                    "rarity": t.rarity,
                    "requires_place": t.requires_place,
                    "constraints": t.constraints
                }
                for t in templates
            ]
        })
