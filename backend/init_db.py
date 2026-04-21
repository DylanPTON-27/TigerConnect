from app import app
from routes.models import db

with app.app_context():
    db.create_all()
