from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .models import Activity, FriendRequest, Friendship, User, db

friends_bp = Blueprint("friends", __name__)


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

    db.session.add(FriendRequest(sender_id=sender, receiver_id=receiver))
    db.session.commit()
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
def get_all_friends():
    user_id = get_jwt_identity()
    all_friends_ids = db.session.query(Friendship.friend_id).filter_by(user_id=user_id).all()
    all_friends_ids = [row[0] for row in all_friends_ids]
    return jsonify(all_friends_ids)


@friends_bp.route("/accept", methods=["POST"])
@jwt_required()
def accept():
    data = request.get_json(silent=True) or {}
    sender = data.get("sender")
    receiver = get_jwt_identity()
    if not sender:
        return {"error": "missing sender"}, 400

    to_delete = FriendRequest.query.filter_by(sender_id=sender, receiver_id=receiver).first()
    if not to_delete:
        return {"error": "request not found"}, 404

    db.session.delete(to_delete)
    friendships = [
        Friendship(user_id=sender, friend_id=receiver),
        Friendship(user_id=receiver, friend_id=sender),
    ]
    db.session.add_all(friendships)
    db.session.commit()
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
    status_object.expires_at = datetime.utcnow() + timedelta(hours=1) if active else datetime.utcnow()
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

    now = datetime.now()
    active_friend_ids = (
        db.session.query(Activity.user_id)
        .filter(Activity.user_id.in_(friend_ids))
        .filter(Activity.is_active.is_(True))
        .filter(Activity.expires_at.isnot(None), Activity.expires_at > now)
        .all()
    )
    return jsonify(active_friend_ids)


@friends_bp.route("/get_status", methods=["POST"])
@jwt_required()
def get_status():
    user_id = get_jwt_identity()
    status_object = Activity.query.filter_by(user_id=user_id).first()
    if not status_object:
        return jsonify(False)

    if status_object.expires_at and status_object.expires_at < datetime.utcnow():
        status_object.is_active = False
        db.session.commit()

    return jsonify(bool(status_object.is_active))
