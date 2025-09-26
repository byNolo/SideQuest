from __future__ import annotations

from flask import Flask
from flask_cors import CORS

from config import Config
from database import Base, engine
from routes import bp as api_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, supports_credentials=True)

    app.register_blueprint(api_bp)

    with app.app_context():
        Base.metadata.create_all(bind=engine)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
