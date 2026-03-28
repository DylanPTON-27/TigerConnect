from flask import Blueprint

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
        receiver_id=receiver
    ).first()

    if existing:
        return {"error": "request already exists"}, 400

    req = FriendRequest(sender_id=sender, receiver_id=receiver)

    db.session.add(req)
    db.session.commit()

    return {"message": "request sent"}