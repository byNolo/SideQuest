from __future__ import annotations

import hashlib
import random
from datetime import date, datetime
from typing import Any

import requests
from flask import jsonify

from auth import login_required, require_user
from database import session_scope
from models import User
from models.quest import Quest
from models.quest_template import QuestTemplate, QuestRarity
from . import bp


def get_weather_data(lat: float, lon: float) -> dict[str, Any]:
    """Fetch current weather data from Open-Meteo API."""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
            "forecast_days": 1,
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        current = data.get("current", {})
        
        # Map weather codes to conditions
        weather_code = current.get("weather_code", 0)
        conditions = []
        
        if weather_code in [0, 1]:  # Clear/mainly clear
            conditions.extend(["clear", "sunny"])
        elif weather_code in [2, 3]:  # Partly/overcast cloudy
            conditions.extend(["cloudy", "overcast"])
        elif weather_code in [45, 48]:  # Fog
            conditions.extend(["fog", "misty"])
        elif weather_code in range(51, 68):  # Rain variants
            conditions.extend(["rainy", "wet"])
        elif weather_code in range(71, 87):  # Snow variants
            conditions.extend(["snowy", "cold"])
        elif weather_code in range(95, 100):  # Thunderstorm
            conditions.extend(["stormy", "dramatic"])
            
        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": weather_code,
            "conditions": conditions,
        }
    except Exception as e:
        # Return default weather if API fails
        return {
            "temperature": None,
            "humidity": None,
            "wind_speed": None,
            "weather_code": 0,
            "conditions": ["clear"],
        }


def find_nearby_places(lat: float, lon: float, radius_km: float = 2.0, place_types: list[str] = None) -> list[dict]:
    """Find nearby places using Overpass API."""
    if not place_types:
        place_types = ["park", "cafe", "shop", "restaurant"]
    
    try:
        # Build Overpass query for multiple amenity types
        overpass_url = "https://overpass-api.de/api/interpreter"
        
        # Convert place types to Overpass amenity tags
        amenity_tags = []
        for place_type in place_types:
            if place_type == "park":
                amenity_tags.extend(["park"])
            elif place_type == "cafe":
                amenity_tags.extend(["cafe", "restaurant"])
            elif place_type == "shop":
                amenity_tags.extend(["shop", "supermarket"])
            elif place_type == "restaurant":
                amenity_tags.extend(["restaurant", "fast_food"])
        
        # Remove duplicates
        amenity_tags = list(set(amenity_tags))
        
        # Build query with radius in meters
        radius_m = int(radius_km * 1000)
        queries = []
        for tag in amenity_tags:
            queries.append(f'node["amenity"="{tag}"](around:{radius_m},{lat},{lon});')
        
        query = f"""
        [out:json][timeout:10];
        (
          {' '.join(queries)}
        );
        out center meta;
        """
        
        response = requests.post(overpass_url, data=query, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        places = []
        
        for element in data.get("elements", [])[:10]:  # Limit to 10 places
            tags = element.get("tags", {})
            name = tags.get("name", f"{tags.get('amenity', 'Place').title()}")
            
            places.append({
                "name": name,
                "lat": element.get("lat"),
                "lon": element.get("lon"),
                "type": tags.get("amenity"),
                "address": tags.get("addr:street", ""),
            })
            
        return places
    except Exception as e:
        return []


def select_quest_template(user: User, weather_data: dict, date_seed: str) -> QuestTemplate | None:
    """Select appropriate quest template based on user preferences and weather."""
    with session_scope() as session:
        # Get active templates
        templates = session.query(QuestTemplate).filter(QuestTemplate.active == True).all()
        
        if not templates:
            return None
            
        # Filter by user preferences
        user_categories = (user.quest_preferences or {}).get("categories", [])
        if user_categories:
            filtered_templates = [t for t in templates if t.category in user_categories]
            if filtered_templates:
                templates = filtered_templates
        
        # Filter by weather conditions
        weather_conditions = weather_data.get("conditions", [])
        weather_compatible = []
        
        for template in templates:
            if not template.weather_conditions:
                # Template works in any weather
                weather_compatible.append(template)
            else:
                # Check if current weather matches template requirements
                if any(condition in weather_conditions for condition in template.weather_conditions):
                    weather_compatible.append(template)
        
        if weather_compatible:
            templates = weather_compatible
        
        # Weighted selection based on rarity and template weight
        weighted_templates = []
        for template in templates:
            # Rarity multiplier
            rarity_weight = {
                QuestRarity.COMMON: 100,
                QuestRarity.RARE: 30,
                QuestRarity.LEGENDARY: 5,
            }.get(template.rarity, 100)
            
            total_weight = template.weight * rarity_weight
            weighted_templates.extend([template] * (total_weight // 10))
        
        if not weighted_templates:
            return templates[0] if templates else None
        
        # Deterministic selection based on user + date
        seed_str = f"{user.username}-{date_seed}"
        seed_hash = hashlib.md5(seed_str.encode()).hexdigest()
        seed_int = int(seed_hash[:8], 16)
        
        random.seed(seed_int)
        return random.choice(weighted_templates)


@bp.get("/today")
@login_required
def todays_quest():
    user = require_user()
    today_date = date.today()
    
    with session_scope() as session:
        # Check if user already has a quest for today
        existing_quest = session.query(Quest).filter(
            Quest.user_id == user.id,
            Quest.date == today_date
        ).first()
        
        if existing_quest:
            # Return existing quest
            return jsonify({"quest": format_quest_response(existing_quest, user)})
        
        # Generate new quest for today
        # Get weather data if user has location
        weather_data = {"conditions": ["clear"]}
        nearby_places = []
        
        if user.default_lat and user.default_lon:
            weather_data = get_weather_data(user.default_lat, user.default_lon)
            nearby_places = find_nearby_places(
                user.default_lat, 
                user.default_lon, 
                user.location_radius_km or 2.0
            )
        
        # Select quest template
        template = select_quest_template(user, weather_data, today_date.isoformat())
        
        # Create quest data
        if not template:
            # Fallback to simple quest if no templates
            generated_context = {
                "title": "Neighborhood Snapshot",
                "description": "Grab your camera and capture something interesting in your area.",
                "hints": ["Look for unique details", "Take your time observing"],
                "location": None,
                "nearby_places": nearby_places,
                "template": None,
                "personalization": {
                    "preferences": user.quest_preferences or {},
                    "privacy": user.privacy,
                }
            }
            template_id = None
        else:
            # Build personalized quest from template
            location_label = user.default_location_name or "your neighborhood"
            
            # Replace placeholders in title and description
            title = template.title.replace("{location}", location_label)
            description = template.description.replace("{location}", location_label)
            
            # Add weather-specific modifications
            if "sunny" in weather_data.get("conditions", []):
                if "outdoor" in template.category:
                    description += " Take advantage of the beautiful weather!"
            elif "rainy" in weather_data.get("conditions", []):
                if "outdoor" in template.category:
                    description += " Don't let the rain stop you - find covered areas or embrace the atmosphere!"
            
            generated_context = {
                "title": title,
                "description": description,
                "hints": template.hints,
                "difficulty": template.difficulty_level,
                "rarity": template.rarity.value,
                "estimated_duration": template.estimated_duration_minutes,
                "category": template.category,
                "location": {
                    "name": user.default_location_name,
                    "lat": user.default_lat,
                    "lon": user.default_lon,
                    "radius_km": user.location_radius_km,
                } if user.default_lat and user.default_lon else None,
                "nearby_places": nearby_places,
                "template": {
                    "id": template.id,
                    "name": template.name,
                    "category": template.category,
                },
                "personalization": {
                    "preferences": user.quest_preferences or {},
                    "privacy": user.privacy,
                }
            }
            template_id = template.id
        
        # Create and save quest record
        new_quest = Quest(
            user_id=user.id,
            date=today_date,
            template_id=template_id,
            seed=None,  # Could add deterministic seed here if needed
            generated_context=generated_context,
            weather_context=weather_data,
            status="assigned",
            delivered_at=datetime.utcnow()
        )
        
        session.add(new_quest)
        session.commit()
        session.refresh(new_quest)
        
        return jsonify({"quest": format_quest_response(new_quest, user)})


def format_quest_response(quest: Quest, user: User) -> dict[str, Any]:
    """Format a Quest object into the response format expected by the frontend."""
    context = quest.generated_context or {}
    
    return {
        "id": quest.id,
        "date": quest.date.isoformat(),
        "title": context.get("title", "Daily Quest"),
        "description": context.get("description", "Complete your daily quest!"),
        "hints": context.get("hints", []),
        "difficulty": context.get("difficulty", 1),
        "rarity": context.get("rarity", "common"),
        "estimated_duration": context.get("estimated_duration"),
        "category": context.get("category"),
        "location": context.get("location"),
        "weather": quest.weather_context or {"conditions": ["clear"]},
        "nearby_places": context.get("nearby_places", []),
        "template": context.get("template"),
        "personalization": context.get("personalization", {}),
        "status": quest.status,
        "delivered_at": quest.delivered_at.isoformat() if quest.delivered_at else None
    }


@bp.get("/quests/templates")
@login_required
def list_templates():
    """List all available quest templates."""
    with session_scope() as session:
        templates = session.query(QuestTemplate).filter(QuestTemplate.active == True).all()
        
        template_data = []
        for template in templates:
            template_data.append({
                "id": template.id,
                "name": template.name,
                "title": template.title,
                "description": template.description,
                "rarity": template.rarity.value,
                "category": template.category,
                "difficulty": template.difficulty_level,
                "estimated_duration": template.estimated_duration_minutes,
                "weather_conditions": template.weather_conditions,
                "location_types": template.location_types,
            })
    
    return jsonify({"templates": template_data})


@bp.post("/quests/admin/seed-templates")
@login_required
def seed_templates():
    """Initialize quest templates with default data."""
    templates_data = [
        {
            "name": "neighborhood_snapshot",
            "title": "Neighborhood Snapshot",
            "description": "Grab your camera (or phone) and capture a detail that makes {location} feel unique today.",
            "rarity": QuestRarity.COMMON,
            "category": "art",
            "hints": [
                "Spend at least 10 minutes observing before documenting.",
                "Share one surprising detail with your future self."
            ],
            "weather_conditions": ["clear", "sunny", "cloudy"],
            "location_types": ["any"],
            "difficulty_level": 1,
            "estimated_duration_minutes": 30,
        },
        {
            "name": "weather_witness",
            "title": "Weather Witness",
            "description": "Document how today's weather is affecting {location}. What changes when the sky shifts?",
            "rarity": QuestRarity.COMMON,
            "category": "outdoor",
            "hints": [
                "Notice how light, shadows, or moisture change the scene.",
                "Compare what you see to yesterday if you can remember."
            ],
            "weather_conditions": ["rainy", "stormy", "snowy", "fog"],
            "location_types": ["outdoor"],
            "difficulty_level": 2,
            "estimated_duration_minutes": 20,
        },
        {
            "name": "urban_explorer",
            "title": "Urban Explorer",
            "description": "Find a corner of {location} you've never properly explored and spend 15 minutes there.",
            "rarity": QuestRarity.RARE,
            "category": "outdoor",
            "hints": [
                "Look up, down, and behind things you usually ignore.",
                "Ask yourself: what story does this place tell?"
            ],
            "weather_conditions": ["clear", "sunny", "cloudy"],
            "location_types": ["urban", "park"],
            "difficulty_level": 3,
            "estimated_duration_minutes": 45,
        },
        {
            "name": "street_artist",
            "title": "Street Artist",
            "description": "Create a quick sketch or photo collage inspired by the textures, colors, or patterns you find in {location}.",
            "rarity": QuestRarity.RARE,
            "category": "art",
            "hints": [
                "Focus on shapes and composition over perfect representation.",
                "Use whatever tools you have - even your phone's photo editor counts!"
            ],
            "weather_conditions": ["clear", "sunny", "cloudy"],
            "location_types": ["any"],
            "difficulty_level": 3,
            "estimated_duration_minutes": 40,
        },
        {
            "name": "social_connection",
            "title": "Social Connection",
            "description": "Strike up a brief, genuine conversation with someone in {location} - a neighbor, shop owner, or fellow explorer.",
            "rarity": QuestRarity.RARE,
            "category": "social",
            "hints": [
                "Start with a genuine compliment or observation about the area.",
                "Listen more than you talk - what do you learn about their perspective?"
            ],
            "weather_conditions": ["clear", "sunny", "cloudy"],
            "location_types": ["cafe", "shop", "park"],
            "difficulty_level": 4,
            "estimated_duration_minutes": 25,
        },
        {
            "name": "seasonal_treasure",
            "title": "Seasonal Treasure Hunt",
            "description": "Find and photograph 3 things in {location} that could only exist in this exact season and weather.",
            "rarity": QuestRarity.LEGENDARY,
            "category": "outdoor",
            "hints": [
                "Think beyond obvious seasonal markers - how do people, light, and activities change?",
                "Create a mini story connecting your three discoveries."
            ],
            "weather_conditions": ["any"],
            "location_types": ["any"],
            "difficulty_level": 4,
            "estimated_duration_minutes": 60,
        },
        {
            "name": "mindful_moment",
            "title": "Mindful Moment",
            "description": "Find a comfortable spot in {location} and spend 10 minutes in focused observation without your phone.",
            "rarity": QuestRarity.COMMON,
            "category": "mindful",
            "hints": [
                "Notice sounds, smells, and textures you usually miss.",
                "Write down 3 things you observed after the 10 minutes."
            ],
            "weather_conditions": ["any"],
            "location_types": ["park", "cafe", "quiet"],
            "difficulty_level": 2,
            "estimated_duration_minutes": 15,
        },
        {
            "name": "flavor_journey",
            "title": "Local Flavor Journey",
            "description": "Try something new from a local business in {location} - a different coffee, snack, or item you've never purchased.",
            "rarity": QuestRarity.COMMON,
            "category": "social",
            "hints": [
                "Ask the staff for their recommendation.",
                "Pay attention to the experience, not just the taste."
            ],
            "weather_conditions": ["any"],
            "location_types": ["cafe", "restaurant", "shop"],
            "difficulty_level": 2,
            "estimated_duration_minutes": 20,
        }
    ]
    
    with session_scope() as session:
        created_count = 0
        for template_data in templates_data:
            # Check if template already exists
            existing = session.query(QuestTemplate).filter(
                QuestTemplate.name == template_data["name"]
            ).first()
            
            if not existing:
                template = QuestTemplate(**template_data)
                session.add(template)
                created_count += 1
    
    return jsonify({"message": f"Created {created_count} new quest templates", "created": created_count})
