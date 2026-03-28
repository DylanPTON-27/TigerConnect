from flask import Blueprint
from flask import jsonify

# Create Blueprint
friends_bp = Blueprint("friends", __name__)

# Friend Requests
@friends_bp.route("/request", methods=["POST"])
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
def notifications():
    data = request.json
    receiver = data["user"]
    all_sender_ids= FriendRequest.session.query(FriendRequest.sender_id).filter_by(
    receiver_id=receiver
    ).all()
    return jsonify(all_sender_ids)

@friends_bp.route("/accept", methods=["POST"])
def accept():
    data = request.json
    sender = data["sender"]
    receiver = data["receiver"]
    to_delete = FriendRequest.query.filter_by(
        sender_id=sender,
        receiver_id=receiver,
    ).first()


    db.session.delete(FriendRequest(sender_id=sender, receiver_id=receiver))
    db.session.add(FriendShip(user_id=sender,friend_id=receiver))
    db.session.add(FriendShip(user_id=receiver,friend_id=sender))
    db.session.commit()
    return {"message": "friendship request accepted"}



@friends_bp.route("/reject", methods=["POST"])
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
def status_update():
    data = request.json
    active=data["active"]
    user_id=data["user"]
    status_object=Activity.query.filter_by(user_id=user_id)
    if active:       
        status_object.is_active=False
    else:
        status_object.is_active=True
    db.session.commit()
    return {"message": "Activity Status Updated"}

@friends_bp.route("/get_status", methods=["POST"])
def get_status():
    data = request.json 
    user_id = data["user"]
    activity_status= FriendRequest.session.query(FriendRequest.user_id).filter_by(
    user_id=user_id
    ).first()
    return jsonify(activity_status)









    

    














