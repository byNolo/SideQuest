"""
Quest generation service - implements weather-aware quest generation with place lookup
"""
import random
import requests
import hashlib
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime
from dataclasses import dataclass
from models import QuestTemplate, Quest, User
from database import SessionLocal
from sqlalchemy import select
from config import Config

@dataclass
class WeatherInfo:
    temperature: float
    condition: str
    tags: List[str]  # sunny, rain, snow, windy, hot, cold
    description: str

@dataclass
class PlaceInfo:
    name: str
    type: str
    lat: float
    lon: float
    distance_km: float

class QuestGenerator:
    def __init__(self):
        self.weather_cache = {}
        self.places_cache = {}
    
    def get_weather(self, lat: float, lon: float) -> Optional[WeatherInfo]:
        """Get current weather from Open-Meteo API"""
        cache_key = f"{lat:.2f},{lon:.2f}"
        if cache_key in self.weather_cache:
            return self.weather_cache[cache_key]
        
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code,wind_speed_10m",
                "timezone": "auto"
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            current = data.get("current", {})
            temp = current.get("temperature_2m", 20)
            weather_code = current.get("weather_code", 0)
            wind_speed = current.get("wind_speed_10m", 0)
            
            # Convert weather code to tags and description
            tags = []
            description = "Clear"
            
            if weather_code == 0:
                tags.append("sunny")
                description = "Clear sky"
            elif weather_code in [1, 2, 3]:
                tags.extend(["partly_cloudy", "sunny"])
                description = "Partly cloudy"
            elif weather_code in [45, 48]:
                tags.append("foggy")
                description = "Foggy"
            elif weather_code in [51, 53, 55, 56, 57]:
                tags.append("drizzle")
                description = "Drizzle"
            elif weather_code in [61, 63, 65, 66, 67]:
                tags.append("rain")
                description = "Rain"
            elif weather_code in [71, 73, 75, 77]:
                tags.append("snow")
                description = "Snow"
            elif weather_code in [80, 81, 82]:
                tags.extend(["rain", "heavy"])
                description = "Heavy rain"
            elif weather_code in [95, 96, 99]:
                tags.extend(["storm", "rain"])
                description = "Thunderstorm"
            
            # Temperature tags
            if temp > 25:
                tags.append("hot")
            elif temp < 0:
                tags.append("cold")
            elif temp < 5:
                tags.append("chilly")
            else:
                tags.append("mild")
            
            # Wind tags
            if wind_speed > 20:
                tags.append("windy")
            
            weather_info = WeatherInfo(
                temperature=temp,
                condition=description,
                tags=tags,
                description=f"{description}, {temp:.0f}°C"
            )
            
            self.weather_cache[cache_key] = weather_info
            return weather_info
            
        except Exception as e:
            print(f"Weather API error: {e}")
            # Fallback weather
            return WeatherInfo(
                temperature=20,
                condition="Unknown",
                tags=["mild"],
                description="Weather unavailable"
            )
    
    def find_places(self, lat: float, lon: float, place_types: List[str], radius_km: float = 2.0) -> List[PlaceInfo]:
        """Find places using Overpass API (OpenStreetMap)"""
        cache_key = f"{lat:.3f},{lon:.3f},{radius_km},{','.join(sorted(place_types))}"
        if cache_key in self.places_cache:
            return self.places_cache[cache_key]
        
        try:
            # Build Overpass query
            overpass_types = {
                "park": "leisure=park",
                "library": "amenity=library", 
                "cafe": "amenity=cafe",
                "restaurant": "amenity=restaurant",
                "shop": "shop~'.*'",
                "museum": "tourism=museum",
                "gallery": "tourism=gallery",
                "market": "amenity=marketplace"
            }
            
            conditions = []
            for place_type in place_types:
                if place_type in overpass_types:
                    conditions.append(overpass_types[place_type])
            
            if not conditions:
                return []
            
            query = f"""
            [out:json][timeout:10];
            (
              node[{"|".join(conditions)}](around:{radius_km * 1000},{lat},{lon});
              way[{"|".join(conditions)}](around:{radius_km * 1000},{lat},{lon});
              relation[{"|".join(conditions)}](around:{radius_km * 1000},{lat},{lon});
            );
            out center 20;
            """
            
            response = requests.post(
                "https://overpass-api.de/api/interpreter",
                data=query,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            places = []
            for element in data.get("elements", [])[:10]:  # Limit to 10 places
                tags = element.get("tags", {})
                name = tags.get("name", "Unnamed location")
                
                # Get coordinates
                if element["type"] == "node":
                    place_lat, place_lon = element["lat"], element["lon"]
                else:
                    center = element.get("center", {})
                    place_lat, place_lon = center.get("lat"), center.get("lon")
                
                if place_lat and place_lon:
                    # Calculate distance
                    distance = self._calculate_distance(lat, lon, place_lat, place_lon)
                    
                    # Determine place type
                    place_type = "unknown"
                    for ptype, condition in overpass_types.items():
                        key = condition.split("=")[0].split("~")[0]
                        if key in tags:
                            place_type = ptype
                            break
                    
                    places.append(PlaceInfo(
                        name=name,
                        type=place_type,
                        lat=place_lat,
                        lon=place_lon,
                        distance_km=distance
                    ))
            
            places.sort(key=lambda p: p.distance_km)
            self.places_cache[cache_key] = places
            return places
            
        except Exception as e:
            print(f"Overpass API error: {e}")
            return []
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in km"""
        import math
        
        R = 6371  # Earth's radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2) * math.sin(dlat/2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon/2) * math.sin(dlon/2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c
    
    def generate_quest_for_user(self, user_id: int, target_date: date = None) -> Optional[Dict]:
        """Generate a quest for a specific user on a specific date"""
        if target_date is None:
            target_date = date.today()
        
        with SessionLocal() as db:
            # Check if quest already exists for this user/date
            existing = db.execute(
                select(Quest).where(Quest.user_id == user_id, Quest.date == target_date)
            ).scalar_one_or_none()
            
            if existing:
                return self._format_quest_response(existing, db)
            
            # Get user info (or create basic user if doesn't exist for debug)
            user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
            if not user:
                # For debug/demo purposes, create a basic user record without explicit ID
                # Let the database assign the ID
                user = User(
                    username=f"user_{user_id}",
                    display_name=f"User {user_id}",
                    privacy="public",
                    prefs={}
                )
                db.add(user)
                db.commit()
                db.refresh(user)
                # Update user_id to match the actual database ID
                user_id = user.id
            
            # Get user location (from prefs or recent location)
            user_prefs = user.prefs or {}
            lat = user_prefs.get("default_lat", 49.2827)  # Default to Vancouver
            lon = user_prefs.get("default_lon", -123.1207)
            
            # Get weather
            weather = self.get_weather(lat, lon)
            
            # Select appropriate templates based on weather and user prefs
            templates = db.execute(
                select(QuestTemplate).where(QuestTemplate.enabled == True)
            ).scalars().all()
            
            if not templates:
                return None
            
            # Filter templates based on weather conditions
            suitable_templates = []
            for template in templates:
                constraints = template.constraints or {}
                
                # Check weather constraints
                if weather and "indoor_bias_if" in constraints:
                    indoor_conditions = constraints["indoor_bias_if"]
                    if any(tag in weather.tags for tag in indoor_conditions):
                        if not template.requires_place:  # Prefer indoor quests in bad weather
                            suitable_templates.append(template)
                        continue
                
                suitable_templates.append(template)
            
            if not suitable_templates:
                suitable_templates = templates
            
            # Weighted selection by rarity
            weights = []
            for template in suitable_templates:
                if template.rarity == "common":
                    weights.append(10)
                elif template.rarity == "rare":
                    weights.append(3)
                elif template.rarity == "legendary":
                    weights.append(1)
                else:
                    weights.append(5)
            
            # Create deterministic seed for reproducible generation
            seed_string = f"{user_id}-{target_date.isoformat()}"
            seed = hashlib.md5(seed_string.encode()).hexdigest()[:16]
            random.seed(int(seed[:8], 16))
            
            # Select template
            selected_template = random.choices(suitable_templates, weights=weights)[0]
            
            # Generate quest context
            context = self._generate_quest_context(selected_template, lat, lon, weather)
            
            # Create quest record
            quest = Quest(
                user_id=user_id,
                date=target_date,
                template_id=selected_template.id,
                seed=seed,
                generated_context=context,
                weather_context={
                    "temperature": weather.temperature if weather else None,
                    "condition": weather.condition if weather else None,
                    "tags": weather.tags if weather else [],
                    "description": weather.description if weather else None
                },
                status="assigned"
            )
            
            db.add(quest)
            db.commit()
            db.refresh(quest)
            
            return self._format_quest_response(quest, db)
    
    def _generate_quest_context(self, template: QuestTemplate, lat: float, lon: float, weather: Optional[WeatherInfo]) -> Dict:
        """Generate specific context for a quest based on template"""
        context = {}
        constraints = template.constraints or {}
        
        # Handle place requirements
        if template.requires_place and "place_types" in constraints:
            place_types = constraints["place_types"]
            radius_range = constraints.get("radius_km_range", [0.5, 2.0])
            radius = random.uniform(radius_range[0], radius_range[1])
            
            places = self.find_places(lat, lon, place_types, radius)
            if places:
                selected_place = random.choice(places[:5])  # Pick from top 5 closest
                context["place"] = {
                    "name": selected_place.name,
                    "type": selected_place.type,
                    "distance_km": round(selected_place.distance_km, 1)
                }
                context["place_type"] = selected_place.type
            else:
                context["place_type"] = random.choice(place_types)
            
            context["radius_km"] = round(radius, 1)
        
        # Handle other dynamic elements
        for key, options in constraints.items():
            if key not in ["place_types", "radius_km_range", "indoor_bias_if"] and isinstance(options, list):
                context[key] = random.choice(options)
        
        # Add weather-specific modifiers
        if weather:
            context["weather"] = weather.description
            if "rain" in weather.tags:
                context["modifier"] = random.choice(["reflections in puddles", "people with umbrellas", "rain drops on glass"])
            elif "sunny" in weather.tags:
                context["modifier"] = random.choice(["interesting shadows", "golden light", "vibrant colors"])
            elif "snow" in weather.tags:
                context["modifier"] = random.choice(["snow patterns", "winter activities", "frost details"])
            else:
                context["modifier"] = random.choice(["interesting textures", "unique angles", "natural framing"])
        
        return context
    
    def _format_quest_response(self, quest: Quest, db) -> Dict:
        """Format quest for API response"""
        template = db.execute(
            select(QuestTemplate).where(QuestTemplate.id == quest.template_id)
        ).scalar_one_or_none()
        
        if not template:
            return None
        
        # Render template with context
        context = quest.generated_context or {}
        
        # Simple template rendering
        body = template.body_template
        for key, value in context.items():
            placeholder = "{" + key + "}"
            if placeholder in body:
                if isinstance(value, dict):
                    body = body.replace(placeholder, str(value.get("name", value)))
                else:
                    body = body.replace(placeholder, str(value))
        
        # Calculate difficulty (1-5 based on rarity and requirements)
        difficulty = 1
        if template.requires_place:
            difficulty += 1
        if template.rarity == "rare":
            difficulty += 1
        elif template.rarity == "legendary":
            difficulty += 2
        
        return {
            "id": quest.id,
            "date": quest.date.isoformat(),
            "title": template.title,
            "details": body,
            "difficulty": min(difficulty, 5),
            "rarity": template.rarity,
            "tags": template.tags,
            "context": context,
            "weather": quest.weather_context,
            "status": quest.status
        }

# Global instance
quest_generator = QuestGenerator()