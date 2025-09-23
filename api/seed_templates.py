"""
Quest template seeding and management
"""
from sqlalchemy.orm import Session
from models import QuestTemplate
from database import SessionLocal

SAMPLE_TEMPLATES = [
    {
        "title": "Neighborhood Snapshot",
        "body_template": "Find a {place_type} within {radius_km} km and capture a creative angle including {modifier}.",
        "tags": ["fast", "no_cost", "requires_place", "photo"],
        "constraints": {
            "place_types": ["park", "library", "cafe", "restaurant"],
            "radius_km_range": [0.3, 2.0],
            "indoor_bias_if": ["rain", "snow"]
        },
        "requires_place": True,
        "rarity": "common"
    },
    {
        "title": "Weather Witness",
        "body_template": "Capture the current weather in an artistic way. Focus on {weather_modifier} and include {composition_rule}.",
        "tags": ["weather", "artistic", "photo", "no_cost"],
        "constraints": {
            "weather_modifiers": ["shadows and light", "reflections", "textures", "movement"],
            "composition_rules": ["rule of thirds", "leading lines", "symmetry", "framing"]
        },
        "requires_place": False,
        "rarity": "common"
    },
    {
        "title": "Urban Explorer",
        "body_template": "Discover a {place_type} you've never been to before within {radius_km} km. Document your experience with a photo and tell us about {discovery_aspect}.",
        "tags": ["exploration", "discovery", "requires_place", "photo"],
        "constraints": {
            "place_types": ["shop", "restaurant", "park", "museum", "gallery", "market"],
            "radius_km_range": [0.5, 3.0],
            "discovery_aspects": ["what surprised you", "the atmosphere", "an interesting detail", "the people you saw"]
        },
        "requires_place": True,
        "rarity": "rare"
    },
    {
        "title": "Street Artist",
        "body_template": "Create or find art in public spaces. This could be street art, graffiti, sculptures, or even temporary art you create yourself. Capture {artistic_focus}.",
        "tags": ["art", "creative", "photo", "public_space"],
        "constraints": {
            "artistic_focus": ["the story behind it", "how it interacts with the environment", "the technique used", "your reaction to it"]
        },
        "requires_place": False,
        "rarity": "rare"
    },
    {
        "title": "Social Connection",
        "body_template": "Strike up a conversation with a stranger (if appropriate and safe) or help someone in your community. Document the experience and share {social_aspect}.",
        "tags": ["social", "community", "human_connection", "story"],
        "constraints": {
            "social_aspects": ["what you learned", "how it made you feel", "what surprised you", "the impact on your day"]
        },
        "requires_place": False,
        "rarity": "legendary"
    },
    {
        "title": "Seasonal Treasure",
        "body_template": "Find something that represents the current season in your area. It could be natural, cultural, or human-made. Capture {seasonal_element} within {time_constraint}.",
        "tags": ["seasonal", "nature", "culture", "time_sensitive", "photo"],
        "constraints": {
            "seasonal_elements": ["colors", "activities", "changes in nature", "festive elements"],
            "time_constraints": ["golden hour", "during lunch break", "early morning", "twilight"]
        },
        "requires_place": False,
        "rarity": "common"
    }
]

def seed_templates():
    """Add sample templates to the database"""
    with SessionLocal() as db:
        # Check if templates already exist
        existing_count = db.query(QuestTemplate).count()
        if existing_count > 0:
            print(f"Templates already exist ({existing_count} found), skipping seed.")
            return
        
        print("Seeding quest templates...")
        for template_data in SAMPLE_TEMPLATES:
            template = QuestTemplate(**template_data)
            db.add(template)
        
        db.commit()
        print(f"Added {len(SAMPLE_TEMPLATES)} quest templates.")

if __name__ == "__main__":
    seed_templates()