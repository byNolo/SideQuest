#!/usr/bin/env python3

from models.quest_template import QuestTemplate, QuestRarity
from database import SessionLocal, engine

def seed_quest_templates():
    """Seed the database with initial quest templates"""
    
    db = SessionLocal()
    
    try:
        # Clear existing templates
        db.query(QuestTemplate).delete()
        db.commit()
        
        templates = [
            {
                'name': 'outdoor_photo_challenge',
                'title': 'Outdoor Photography Challenge',
                'description': 'Take a creative photo of {place_type} in your area',
                'category': 'photography',
                'location_types': ['park', 'garden', 'nature_reserve'],
                'weather_conditions': ['clear', 'partly_cloudy'],
                'difficulty_level': 2,
                'rarity': QuestRarity.COMMON,
                'estimated_duration_minutes': 45,
                'constraints': {
                    'tags': ['photography', 'outdoor', 'nature'],
                    'equipment_needed': 'Camera or smartphone'
                }
            },
            {
                'name': 'history_explorer',
                'title': 'Local History Explorer',
                'description': 'Visit {place_name} and learn about its historical significance',
                'category': 'education',
                'location_types': ['museum', 'memorial', 'historic'],
                'weather_conditions': ['clear', 'partly_cloudy', 'overcast'],
                'difficulty_level': 3,
                'rarity': QuestRarity.COMMON,
                'estimated_duration_minutes': 90,
                'constraints': {
                    'tags': ['history', 'education', 'culture']
                }
            },
            {
                'name': 'rainy_day_adventure',
                'title': 'Rainy Day Adventure',
                'description': 'Explore an indoor {place_type} and discover something new',
                'category': 'exploration',
                'location_types': ['museum', 'library', 'shopping_centre'],
                'weather_conditions': ['rain', 'overcast'],
                'difficulty_level': 1,
                'rarity': QuestRarity.COMMON,
                'estimated_duration_minutes': 120,
                'constraints': {
                    'tags': ['indoor', 'learning', 'exploration'],
                    'equipment_needed': 'Umbrella for travel'
                }
            },
            {
                'name': 'culinary_quest',
                'title': 'Culinary Quest',
                'description': 'Try a new cuisine at {place_name} and rate your experience',
                'category': 'food',
                'location_types': ['restaurant', 'cafe', 'food_court'],
                'weather_conditions': ['clear', 'partly_cloudy', 'overcast', 'rain'],
                'difficulty_level': 2,
                'rarity': QuestRarity.COMMON,
                'estimated_duration_minutes': 90,
                'constraints': {
                    'tags': ['food', 'social', 'adventure'],
                    'equipment_needed': 'Appetite and curiosity'
                }
            },
            {
                'name': 'perfect_weather_walk',
                'title': 'Perfect Weather Walk',
                'description': 'Take a scenic walk through {place_name} and enjoy the {weather} weather',
                'category': 'wellness',
                'location_types': ['park', 'trail', 'waterfront'],
                'weather_conditions': ['clear', 'partly_cloudy'],
                'difficulty_level': 1,
                'rarity': QuestRarity.COMMON,
                'estimated_duration_minutes': 60,
                'constraints': {
                    'tags': ['walking', 'exercise', 'nature', 'wellness'],
                    'equipment_needed': 'Comfortable walking shoes'
                }
            },
            {
                'name': 'community_connection',
                'title': 'Community Connection',
                'description': 'Volunteer or attend an event at {place_name} to meet locals',
                'category': 'social',
                'location_types': ['community_centre', 'library', 'school'],
                'weather_conditions': ['clear', 'partly_cloudy', 'overcast'],
                'difficulty_level': 4,
                'rarity': QuestRarity.RARE,
                'estimated_duration_minutes': 180,
                'constraints': {
                    'tags': ['social', 'community', 'volunteering'],
                    'equipment_needed': 'Good attitude and willingness to help'
                }
            },
            {
                'name': 'urban_explorer',
                'title': 'Urban Explorer',
                'description': 'Discover hidden gems near {place_name} and document your findings',
                'category': 'exploration',
                'location_types': ['shopping_centre', 'town_hall', 'post_office'],
                'weather_conditions': ['clear', 'partly_cloudy', 'overcast'],
                'difficulty_level': 3,
                'rarity': QuestRarity.RARE,
                'estimated_duration_minutes': 150,
                'constraints': {
                    'tags': ['exploration', 'urban', 'discovery'],
                    'equipment_needed': 'Camera, notebook, curiosity'
                }
            },
            {
                'name': 'legendary_challenge',
                'title': 'Legendary Challenge',
                'description': 'Complete a challenging adventure at {place_name} during {weather} conditions',
                'category': 'challenge',
                'location_types': ['park', 'trail', 'nature_reserve'],
                'weather_conditions': ['rain', 'snow'],
                'difficulty_level': 5,
                'rarity': QuestRarity.LEGENDARY,
                'estimated_duration_minutes': 300,
                'constraints': {
                    'tags': ['challenge', 'adventure', 'weather'],
                    'equipment_needed': 'Weather-appropriate gear, determination'
                }
            }
        ]
        
        # Create templates
        for template_data in templates:
            template = QuestTemplate(**template_data)
            db.add(template)
        
        db.commit()
        print(f"Successfully seeded {len(templates)} quest templates")
        
        # Print summary
        for rarity in QuestRarity:
            count = db.query(QuestTemplate).filter(QuestTemplate.rarity == rarity).count()
            print(f"{rarity.value}: {count} templates")
            
    except Exception as e:
        db.rollback()
        print(f"Error seeding templates: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_quest_templates()