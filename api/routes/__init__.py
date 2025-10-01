from flask import Blueprint

bp = Blueprint("api", __name__, url_prefix="/api")

# Import route modules so they register their handlers with the blueprint
from . import auth, health, onboarding, quests, media, submissions  # noqa: E402,F401
