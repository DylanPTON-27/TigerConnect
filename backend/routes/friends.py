from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename
from .models import Activity, FriendRequest, Friendship, User, db, Blocked, UserImage
import os 
import sendgrid
from sendgrid.helpers.mail import Mail
import re



friends_bp = Blueprint("friends", __name__)


def send_email(recipient, body):
    client = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
    message = Mail(
        from_email="jasincekinmez@gmail.com",
        to_emails=recipient,
        subject="Friend Request",
        html_content=body
    )
    client.send(message)

@friends_bp.route("/request", methods=["POST"])
@jwt_required()
def send_request():
    data = request.get_json(silent=True) or {}
    sender = get_jwt_identity()
    receiver = data.get("receiver")
    if not receiver:
        return {"error": "missing receiver"}, 400
    receiver = receiver.strip().lower()
    if not receiver:
        return {"error": "missing receiver"}, 400

    pattern = r'[A-Za-z]{2}[0-9]{4}'
    valid_netid = bool(re.fullmatch(pattern, sender))
    if not valid_netid:
         return {"error": "not valid netid"}, 400



    if receiver == sender:
        return {"error": "cannot friend yourself"}, 400

    # Demo-friendly: ensure receiver exists to satisfy FK constraints.
    sender_user = User.query.filter_by(netid=sender).first()
    if not sender_user:
        db.session.add(User(netid=sender, name=sender, email=f"{sender}@princeton.edu"))
    receiver_user = User.query.filter_by(netid=receiver).first()
    if not receiver_user:
        db.session.add(User(netid=receiver, name=receiver, email=f"{receiver}@princeton.edu"))

    existing = FriendRequest.query.filter_by(sender_id=sender, receiver_id=receiver).first()
    if existing:
        return {"error": "request already exists"}, 400
    blocked = Blocked.query.filter_by(user_id=sender, friend_id=receiver).first()
    blocked2 = Blocked.query.filter_by(user_id=receiver, friend_id=sender).first()
    if blocked:
        return {"error": "Unblock the person you want to friend first"}, 400
    if blocked2:
        return {"error": "Try again later!"}, 400



    db.session.add(FriendRequest(sender_id=sender, receiver_id=receiver))
    db.session.commit()
    send_email(f"{receiver}@princeton.edu",f"{sender} sent you a friend request")
    return {"message": "request sent"}


@friends_bp.route("/notifications", methods=["POST"])
@jwt_required()
def notifications():
    receiver = get_jwt_identity()
    all_sender_ids = db.session.query(FriendRequest.sender_id).filter_by(receiver_id=receiver).all()
    sender_ids = [row[0] for row in all_sender_ids]
    return jsonify(sender_ids)


@friends_bp.route("/get_all_friends", methods=["POST"])
@jwt_required()
def get_all_friends_route():
    return jsonify(
        get_all_friends(get_jwt_identity())
    )


def get_all_friends(user_id):
    all_friends_ids = db.session.query(Friendship.friend_id).filter_by(user_id=user_id).all()
    all_friends_ids = [row[0] for row in all_friends_ids]
    return all_friends_ids


@friends_bp.route("/accept", methods=["POST"])
@jwt_required()
def accept():
    sender = (request.form.get("sender")).strip().lower()
    print(sender)
    receiver = get_jwt_identity()
    if not sender:
        return {"error": "missing sender"}, 400
    if Blocked.query.filter_by(user_id=receiver, friend_id=sender).first():
        return {"error": "Sender is blocked"}, 400

    to_delete = FriendRequest.query.filter_by(sender_id=sender, receiver_id=receiver).first()
    if not to_delete:
        return {"error": "request not found"}, 404

    # Ensure users exist (defensive for old/partial data states).
    sender_user = User.query.filter_by(netid=sender).first()
    if not sender_user:
        db.session.add(User(netid=sender, name=sender, email=f"{sender}@princeton.edu"))
    receiver_user = User.query.filter_by(netid=receiver).first()
    if not receiver_user:
        db.session.add(User(netid=receiver, name=receiver, email=f"{receiver}@princeton.edu"))

    existing_forward = Friendship.query.filter_by(user_id=sender, friend_id=receiver).first()
    existing_reverse = Friendship.query.filter_by(user_id=receiver, friend_id=sender).first()

    db.session.delete(to_delete)
    if not existing_forward:
        db.session.add(Friendship(user_id=sender, friend_id=receiver))
    if not existing_reverse:
        db.session.add(Friendship(user_id=receiver, friend_id=sender))

    try:
        db.session.commit()
    except IntegrityError:
        # Handle duplicate/constraint races gracefully for demo and prod.
        db.session.rollback()

        # If friendship rows now exist, treat this as success and just remove pending request.
        now_forward = Friendship.query.filter_by(user_id=sender, friend_id=receiver).first()
        now_reverse = Friendship.query.filter_by(user_id=receiver, friend_id=sender).first()
        if now_forward and now_reverse:
            pending = FriendRequest.query.filter_by(sender_id=sender, receiver_id=receiver).first()
            if pending:
                db.session.delete(pending)
                db.session.commit()
            return {"message": "friendship request accepted"}

        return {"error": "failed to accept request due to data integrity"}, 400

    return {"message": "friendship request accepted"}


@friends_bp.route("/reject", methods=["POST"])
@jwt_required()
def reject():
    data = request.get_json(silent=True) or {}
    sender = data.get("sender")
    receiver = get_jwt_identity()
    if not sender:
        return {"error": "missing sender"}, 400

    to_delete = FriendRequest.query.filter_by(sender_id=sender, receiver_id=receiver).first()
    if not to_delete:
        return {"error": "request not found"}, 404

    db.session.delete(to_delete)
    db.session.commit()
    return {"message": "friendship request rejected"}


@friends_bp.route("/status_update", methods=["POST"])
@jwt_required()
def status_update():
    data = request.get_json(silent=True) or {}
    active = bool(data.get("active", False))
    user_id = get_jwt_identity()

    status_object = Activity.query.filter_by(user_id=user_id).first()
    if not status_object:
        status_object = Activity(user_id=user_id)
        db.session.add(status_object)

    status_object.is_active = active
    status_object.expires_at = datetime.now() + timedelta(hours=1) if active else datetime.now()
    db.session.commit()
    return {"message": "Activity Status Updated"}


@friends_bp.route("/get_active_friends", methods=["POST"])
@jwt_required()
def get_active_friends():
    user_id = get_jwt_identity()
    friend_rows = db.session.query(Friendship.friend_id).filter_by(user_id=user_id).all()
    friend_ids = [row[0] for row in friend_rows]
    if not friend_ids:
        return jsonify([])

    now = datetime.utcnow()
    active_friend_ids = (
        db.session.query(Activity.user_id)
        .filter(Activity.user_id.in_(friend_ids))
        .filter(Activity.is_active.is_(True))
        .filter(Activity.expires_at.isnot(None), Activity.expires_at > now)
        .all()
    )
    return jsonify(active_friend_ids)


@friends_bp.route("/remove", methods=["POST"])
@jwt_required()
def remove():
    data = request.get_json(silent=True) or {}
    user_id = get_jwt_identity() 
    receiver = (data.get("receiver"))

    if not receiver:
        return {"error": "missing receiver"}, 400

    forward = Friendship.query.filter_by(user_id=user_id, friend_id=receiver).first()
    reverse = Friendship.query.filter_by(user_id=receiver, friend_id=user_id).first()

    if not forward and not reverse:
        return {"error": "friendship not found"}, 404
    db.session.delete(forward)
    db.session.delete(reverse)

    db.session.commit()
    return {"message": "friendship removed"}

    
@friends_bp.route("/get_friends_and_status", methods=["POST"])
@jwt_required()
def get_friends_and_status():
    user_id = get_jwt_identity()
    now = datetime.utcnow()

    # 1. Join Friendship with Activity
    # We use a outerjoin (Left Join) so friends without activity still show up
    results = (
        db.session.query(
            Friendship.friend_id,
            Activity.is_active,
            Activity.expires_at
        )
        .outerjoin(Activity, Friendship.friend_id == Activity.user_id)
        .filter(Friendship.user_id == user_id)
        .all()
    )

    friends_status = []
    for friend_id, is_active, expires_at in results:
        # 2. Logic to determine status based on activity and expiration
        # Status is true only if is_active is True AND it hasn't expired yet
        is_currently_active = (
            is_active is True and 
            expires_at is not None and 
            expires_at > now
        )

        friends_status.append({
            "friend_id": friend_id,
            "status": "active" if is_currently_active else "offline"
        })

    return jsonify(friends_status)

@friends_bp.route("/get_status", methods=["POST"])
@jwt_required()
def get_status():
    user_id = get_jwt_identity()
    status_object = Activity.query.filter_by(user_id=user_id).first()
    if not status_object:
        return jsonify(False)

    if status_object.expires_at and status_object.expires_at < datetime.now():
        status_object.is_active = False
        db.session.commit()

    return jsonify(bool(status_object.is_active))

@friends_bp.route("/block", methods=["POST"])
@jwt_required()
def block():
    data = request.get_json(silent=True) or {}
    user_id = get_jwt_identity() 
    receiver = (data.get("receiver"))

    if not receiver:
        return {"error": "missing receiver"}, 400
    

    found = Blocked.query.filter_by(user_id=user_id, friend_id=receiver).first()
    if found:
        return {"error": "Already blocked"}, 400

    forward = Friendship.query.filter_by(user_id=user_id, friend_id=receiver).first()
    reverse = Friendship.query.filter_by(user_id=receiver, friend_id=user_id).first()

    if forward:
        db.session.delete(forward)
    if reverse:
        db.session.delete(reverse)
    
    request1 = FriendRequest.query.filter_by(sender_id=user_id, receiver_id=receiver).first()
    request2 = FriendRequest.query.filter_by(sender_id=receiver, receiver_id=user_id).first()

    if request1:
        db.session.delete(request1)
    if request2:
        db.session.delete(request2)
    
    db.session.add(Blocked(user_id=user_id, friend_id=receiver))
    db.session.commit()
    return {"message": "friend blocked"}


@friends_bp.route("/unblock", methods=["POST"])
@jwt_required()
def unblock():
    data = request.get_json(silent=True) or {}
    user_id = get_jwt_identity() 
    receiver = (data.get("receiver"))

    if not receiver:
        return {"error": "missing receiver"}, 400



    found = Blocked.query.filter_by(user_id=user_id, friend_id=receiver).first()
    if not found:
        return {"error": "Not blocked"}, 400
    
    db.session.delete(found)
    db.session.commit()
    return {"message": "friend unblocked"}

@friends_bp.route("/update_photo", methods=["POST"])
@jwt_required()
def update_photo():
    user_id = get_jwt_identity() 
    photo = request.files.get('image')

    if not photo:
        return jsonify({"error": "No Image Uploaded!"}), 400

    existing_image = UserImage.query.filter_by(user_id=user_id).first()

    if existing_image:
        existing_image.name = secure_filename(photo.filename)
        existing_image.mimetype = photo.mimetype
        existing_image.data = photo.read()
        message = "Image updated successfully!"
    else:
        new_image = UserImage(
            user_id=user_id,
            name=secure_filename(photo.filename),
            mimetype=photo.mimetype,
            data=photo.read()
        )
        db.session.add(new_image)
        message = "New image created!"

    db.session.commit()
    
    return jsonify({"message": message}), 200
    
@friends_bp.route("/get_photo", methods=["POST"])
@jwt_required()
def get_photo():
    user_id = get_jwt_identity() 

    photo = UserImage.query.filter_by(user_id = user_id).first()

    return Response(
        photo.data, 
        mimetype=photo.mimetype
    )