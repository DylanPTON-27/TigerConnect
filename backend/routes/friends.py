from flask import Blueprint, request
from flask import jsonify
from models import db, FriendRequest, Friendship, Activity
<<<<<<< HEAD
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
=======
import datetime
>>>>>>> d5465e5 (fixed some layout issues)

# Create Blueprint
friends_bp = Blueprint("friends", __name__)

@friends_bp.route("/request", methods=["POST"])
@jwt_required()
def send_request():
    data = request.json
    sender = data["sender"]
    receiver = data["receiver"]

    # prevent duplicates
    existing = FriendRequest.query.filter_by(
        sender_id=sender,
        receiver_id=receiver,
    ).first()

    if existing:
        return {"error": "request already exists"}, 400

    req = FriendRequest(sender_id=sender, receiver_id=receiver)

    db.session.add(req)
    db.session.commit()

    return {"message": "request sent"}

@friends_bp.route("/notifications", methods=["POST"])
@jwt_required()
def notifications():
    data = request.json
    receiver = data["user"]
    all_sender_ids= FriendRequest.session.query(FriendRequest.sender_id).filter_by(
    receiver_id=receiver
    ).all()
    return jsonify(all_sender_ids)

@friends_bp.route("/get_all_friends", methods=["POST"])
@jwt_required()
def get_all_friends():
    data = request.json
    user_id = data['user']
    all_friends_ids=Friendship.session.query(Friendship.friend_id).filter_by(user_id=user_id).all()
    return jsonify(all_friends_ids)



@friends_bp.route("/accept", methods=["POST"])
@jwt_required()
def accept():
    data = request.json
    sender = data["sender"]
    receiver = data["receiver"]
    to_delete = FriendRequest.query.filter_by(
        sender_id=sender,
        receiver_id=receiver,
    ).first()


    db.session.delete(FriendRequest(sender_id=sender, receiver_id=receiver))
    db.session.add(Friendship(user_id=sender,friend_id=receiver))
    db.session.add(Friendship(user_id=receiver,friend_id=sender))
    db.session.commit()
    return {"message": "friendship request accepted"}



@friends_bp.route("/reject", methods=["POST"])
@jwt_required()
def reject():
    data = request.json
    sender = data["sender"]
    receiver = data["receiver"]
    to_delete = FriendRequest.query.filter_by(
        sender_id=sender,
        receiver_id=receiver,
    ).first()
    db.session.delete(FriendRequest(sender_id=sender, receiver_id=receiver))
    db.session.commit()
    return {"message": "friendship request accepted"}

@friends_bp.route("/status_update", methods=["POST"])
@jwt_required()
def status_update():
    data = request.json
    active=data["active"]
    user_id=data["user"]
    status_object=Activity.query.filter_by(user_id=user_id)
    if active:       
        status_object.is_active=False
        status_object.expires_at=datetime.utcnow()
    else:
        status_object.is_active=True
        status_object.expires_at=datetime.utcnow() + timedelta(hours=1)

    db.session.commit()
    return {"message": "Activity Status Updated"}


@friends_bp.route("/get_active_friends", methods=["POST"])
@jwt_required()
def get_active_friends():
    data = request.json
    user_id = data['user']
    solely_users=Friendship.query.filter_by(user_id=user_id)
    joined_table = solely_users.join(Activity,Friendship.friend_id == Activity.user_id)
    active_friend_ids=joined_table.session.query(friend_id).all()
    return jsonify(all_friends_ids)




@friends_bp.route("/get_status", methods=["POST"])
@jwt_required()
def get_status():
    data = request.json 
    user_id = data["user"]
    status_object=Activity.query.filter_by(user_id=user_id).first()
    if status_object.expires_at<datetime.utcnow():
        status_object.is_active=False
        db.session.commit()
    return jsonify(True)
   
