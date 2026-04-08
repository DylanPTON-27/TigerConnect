from app import app
from models import db, User, FriendRequest, Friendship, Activity

with app.app_context():
    db.create_all()