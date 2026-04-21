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
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False)
    friend_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False)

# Activity Status
class Activity(db.Model):
    user_id = db.Column(db.String, db.ForeignKey("user.netid"), primary_key=True)
    is_active = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)

# Blocked People 
class Blocked(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False)
    friend_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False)

# Calendar OAuth account (Google)
class CalendarAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False, unique=True)
    provider = db.Column(db.String(20), nullable=False, default="google")
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

# Normalized calendar events
class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False, index=True)
    provider_event_id = db.Column(db.String(255), nullable=False, index=True)
    title = db.Column(db.String(255))
    start_utc = db.Column(db.DateTime, nullable=False, index=True)
    end_utc = db.Column(db.DateTime, nullable=False, index=True)
    timezone = db.Column(db.String(64))
    updated_at = db.Column(db.DateTime, default=datetime.now())

    __table_args__ = (
        db.UniqueConstraint("user_id", "provider_event_id", name="uq_user_event"),
    )

# AuthNonce handoff
class AuthNonce(db.Model):
    nonce = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)

class UserImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("user.netid"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mimetype = db.Column(db.String(20), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

class Calendar(db.Model):
    __tablename__ = 'calendars'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String, nullable=False, unique=True)
    filename = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
