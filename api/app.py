from flask import Flask
from flask_cors import CORS
from config import Config
from database import engine, Base
from routes import bp

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.register_blueprint(bp)

# Create tables on first run (dev only)
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
