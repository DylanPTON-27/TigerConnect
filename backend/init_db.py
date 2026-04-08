from app import app
from routes.models import db, User, FriendRequest, Friendship, Activity

with app.app_context():
    db.create_all()