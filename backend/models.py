from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Users
class User(db.Model):
    netid = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

# Friend Requests
class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False)
    receiver_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Friendship Status
class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False, primary_key = True)
    friend_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False)

# Activity Status
class Activity(db.Model):
    user_id = db.Column(db.String, db.ForeignKey("user.netid"), primary_key=True)
    is_active = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)