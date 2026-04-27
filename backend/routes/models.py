from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

# Users
class Users(db.Model):
    netid = db.Column(db.String, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))

# Friend Requests
class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)
    receiver_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

# Friendship Status
class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)
    friend_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)

# Conversations
class Conversation(db.Model):
    # Store the UUID as the primary key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4())) 
    user_one = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)
    user_two = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (db.UniqueConstraint('user_one', 'user_two', name='unique_chat_pair'),)

# Activity Status
class Activity(db.Model):
    user_id = db.Column(db.String, db.ForeignKey("users.netid"), primary_key=True)
    is_active = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime)

# Blocked People 
class Blocked(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)
    friend_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)

# Calendar OAuth account (Google)
class CalendarAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False, unique=True)
    provider = db.Column(db.String(20), nullable=False, default="google")
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)

# Normalized calendar events
class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False, index=True)
    provider_event_id = db.Column(db.String(255), nullable=False, index=True)
    title = db.Column(db.String(255))
    start_utc = db.Column(db.DateTime, nullable=False, index=True)
    end_utc = db.Column(db.DateTime, nullable=False, index=True)
    timezone = db.Column(db.String(64))
    updated_at = db.Column(db.DateTime, default=datetime.now)

    __table_args__ = (
        db.UniqueConstraint("user_id", "provider_event_id", name="uq_user_event"),
    )

# AuthNonce handoff
class AuthNonce(db.Model):
    nonce = db.Column(db.String(64), primary_key=True)
    username = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

# Profile Pics
class UserImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey("users.netid"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    mimetype = db.Column(db.String(20), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False)

# Calendars
class Calendar(db.Model):
    __tablename__ = 'calendars'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String, nullable=False, unique=True)
    filename = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
