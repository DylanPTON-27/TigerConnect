from datetime import datetime, timedelta
import io
from PIL import Image
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_
from werkzeug.utils import secure_filename
from .models import Activity, FriendRequest, Friendship, Users, db, Blocked, UserImage, Conversation
import base64
import requests
import uuid
import os 
import sendgrid
from sendgrid.helpers.mail import Mail
import time
import jwt


friends_bp = Blueprint("friends", __name__)

TALKJS_SECRET_KEY = os.environ.get('TALKJS_SECRET_KEY', 'change-pls')
TALKJS_APP_ID = os.environ.get('TALKJS_APP_ID', 'foobar')


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
    print(data)
    sender = get_jwt_identity()
    receiver = data.get("receiver")
    print(sender, receiver)
    if not receiver:
        return {"error": "Missing receiver"}, 400
    receiver = receiver.strip().lower()
    if not receiver:
        return {"error": "Missing receiver"}, 400

    if receiver == sender:
        return {"error": "Cannot friend yourself"}, 400
    
    friended = Friendship.query.filter(
        or_(
            and_(Friendship.user_id==sender, Friendship.friend_id==receiver), 
            and_(Friendship.user_id==receiver, Friendship.friend_id==sender)
        )
    ).first()
    if friended:
        return {"error": "Already a friend"}, 400

    sender_user = Users.query.filter_by(netid=sender).first()
    if not sender_user:
        return {"error": "Invalid sender"}, 400
    receiver_user = Users.query.filter_by(netid=receiver).first()
    if not receiver_user:
        return {"error": "User does not exist"}, 400

    existing = FriendRequest.query.filter(
        or_(
            and_(FriendRequest.sender_id == sender, FriendRequest.receiver_id == receiver),
            and_(FriendRequest.sender_id == receiver, FriendRequest.receiver_id == sender)
        )
    ).first()
    if existing:
        return {"error": "Request already exists"}, 400
    blocked = Blocked.query.filter_by(user_id=sender, friend_id=receiver).first()
    blocked2 = Blocked.query.filter_by(user_id=receiver, friend_id=sender).first()
    if blocked:
        db.session.delete(blocked)
    if blocked2:
        return {"error": "Try again later!"}, 400

    db.session.add(FriendRequest(sender_id=sender, receiver_id=receiver))
    db.session.commit()
    # send_email(f"{receiver}@princeton.edu",f"{sender} sent you a friend request")
    return {"message": "request sent"}, 200

@friends_bp.route("/notifications", methods=["POST"])
@jwt_required()
def notifications():
    receiver = get_jwt_identity()
    senders = (
        db.session.query(FriendRequest.sender_id, Users.name)
        .join(Users, FriendRequest.sender_id == Users.netid)
        .filter(FriendRequest.receiver_id == receiver)
        .all()
    )
    sender_list = [
        {"netid": sender_id, "name": name}
        for sender_id, name in senders
    ]
    return jsonify(sender_list)

def get_all_friends(user_id):
    all_friends_ids = db.session.query(Friendship.friend_id).filter_by(user_id=user_id).all()
    all_friends_ids = [row[0] for row in all_friends_ids]
    return all_friends_ids

@friends_bp.route("/accept", methods=["POST"])
@jwt_required()
def accept():
    data = request.get_json(silent=True) or {}
    sender = data.get("sender")
    receiver = get_jwt_identity()
    if not sender:
        return {"error": "missing sender"}, 400
    
    if Blocked.query.filter_by(user_id=receiver, friend_id=sender).first():
        return {"error": "Sender is blocked"}, 400

    to_delete = FriendRequest.query.filter_by(sender_id=sender, receiver_id=receiver).first()
    if not to_delete:
        return {"error": "request not found"}, 404

    # Ensure users exist (defensive for old/partial data states).
    sender_user = Users.query.filter_by(netid=sender).first()
    if not sender_user:
        db.session.add(Users(netid=sender, name=sender, email=f"{sender}@princeton.edu"))
    receiver_user = Users.query.filter_by(netid=receiver).first()
    if not receiver_user:
        db.session.add(Users(netid=receiver, name=receiver, email=f"{receiver}@princeton.edu"))

    existing_forward = Friendship.query.filter_by(user_id=sender, friend_id=receiver).first()
    existing_reverse = Friendship.query.filter_by(user_id=receiver, friend_id=sender).first()

    db.session.delete(to_delete)

    new_friendships = []
    if not existing_forward:
        new_friendships.append(Friendship(user_id=sender, friend_id=receiver))
    if not existing_reverse:
        new_friendships.append(Friendship(user_id=receiver, friend_id=sender))

    try:
        db.session.add_all(new_friendships)
        db.session.commit()
    except IntegrityError as e:
        print(e)
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

    
@friends_bp.route("/get_everything", methods=["POST"])
@jwt_required()
def get_everything():
    user_id = get_jwt_identity()
    now = datetime.now()

    results = (
        db.session.query(
            Friendship.friend_id,
            Users.name,
            Activity.is_active,
            Activity.expires_at,
            UserImage.data,
            UserImage.mimetype
        )
        .join(Users, Friendship.friend_id == Users.netid)
        .outerjoin(Activity, Friendship.friend_id == Activity.user_id)
        .outerjoin(UserImage, Friendship.friend_id == UserImage.user_id) # Join photos
        .filter(Friendship.user_id == user_id)
        .all()
    )

    friends_status = []
    for friend_id, name, is_active, expires_at, img_data, mimetype in results:
        is_currently_active = (
            is_active is True and 
            expires_at is not None and 
            expires_at > now
        )

        # Handle the image data conversion
        photo_url = ""
        if img_data:
            # Convert binary to base64 string for JSON
            encoded_img = base64.b64encode(img_data).decode('utf-8')
            photo_url = f"data:{mimetype};base64,{encoded_img}"

        friends_status.append({
            "netid": friend_id,
            "name": name,
            "status": "active" if is_currently_active else "offline",
            "photoUrl": photo_url
        })

    all_user_rows = db.session.query(Users.netid, Users.name).all()
    
    all_users_list = [
        {"value": row.netid, "label": row.name} 
        for row in all_user_rows
    ]

    blocked_rows = (
        db.session.query(Blocked.friend_id, Users.name)
        .join(Users, Blocked.friend_id == Users.netid)
        .filter(Blocked.user_id == user_id)
        .all()
    )
    blocked_list = [
        {"netid": friend_id, "name": name}
        for friend_id, name in blocked_rows
    ]

    sent_requests = (
        db.session.query(FriendRequest.receiver_id, Users.name)
        .join(Users, FriendRequest.receiver_id == Users.netid)
        .filter(FriendRequest.sender_id == user_id)
        .all()
    )
    sent_list = [
        {"netid": receiver_id, "name": name}
        for receiver_id, name in sent_requests
    ]

    return jsonify({
        "friends": friends_status,
        "all_users": all_users_list,
        "blocked": blocked_list,
        "sent_requests": sent_list,
    })

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

@friends_bp.route("/withdraw_request", methods=["POST"])
@jwt_required()
def withdraw_request():
    user_id = get_jwt_identity()
    data = request.get_json(silent=True) or {}
    receiver = data.get("receiver")

    if not receiver:
        return {"error": "missing receiver"}, 400

    request_to_delete = FriendRequest.query.filter_by(sender_id=user_id, receiver_id=receiver).first()
    if not request_to_delete:
        return {"error": "friend request not found"}, 404

    db.session.delete(request_to_delete)
    db.session.commit()
    return {"message": "friend request withdrawn"}

@friends_bp.route("/update_photo", methods=["POST"])
@jwt_required()
def update_photo():
    user_id = get_jwt_identity() 
    photo = request.files.get('image')

    if photo is None:
        return jsonify({"error": "No Image Uploaded!"}), 400

    try:
        img = Image.open(photo)
        
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        img.thumbnail((200, 200))

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85) 
        shrunk_data = buffer.getvalue()
        
    except Exception as e:
        return jsonify({"error": f"Failed to process image: {str(e)}"}), 400

    existing_image = UserImage.query.filter_by(user_id=user_id).first()

    if existing_image:
        existing_image.name = secure_filename(photo.filename)
        existing_image.mimetype = "image/jpeg"
        existing_image.data = shrunk_data
        message = "Image updated successfully!"
    else:
        new_image = UserImage(
            user_id=user_id,
            name=secure_filename(photo.filename),
            mimetype="image/jpeg",
            data=shrunk_data
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
    if photo is None:
        return jsonify({"error": "No profile photo found"}), 404

    return Response(
        photo.data, 
        mimetype=photo.mimetype
    )

@friends_bp.route('/get-talkjs-token', methods=["POST"])
@jwt_required()
def get_talkjs_token():
    user_id = get_jwt_identity()

    payload = {
        "tokenType": "user",
        "iss": TALKJS_APP_ID,
        "sub": user_id,
        "iat": int(time.time()), # Issued At
        "exp": int(time.time()) + 24 * 3600 # Expires in 24 hours
    }

    try:
        encoded_jwt = jwt.encode(payload, TALKJS_SECRET_KEY, algorithm="HS256")
        
        return jsonify({
            "token": encoded_jwt,
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@friends_bp.route('/conversations', methods=["POST"])
@jwt_required()
def conversations():
    current_user_id = get_jwt_identity()
    
    friendships = Friendship.query.filter((Friendship.user_id == current_user_id)).all()

    friend_ids = [f.friend_id for f in friendships]

    existing_convs = Conversation.query.filter(
        (Conversation.user_one == current_user_id) | (Conversation.user_two == current_user_id)
    ).all()

    chat_map = {}
    for conv in existing_convs:
        other_party = conv.user_two if conv.user_one == current_user_id else conv.user_one
        chat_map[other_party] = conv.id

    results = {}

    for f_id in friend_ids:
        if f_id in chat_map:
            results[f_id] = chat_map[f_id]
        else:
            new_uuid = str(uuid.uuid4())
            try:
                talkjs_url = f"https://api.talkjs.com/v1/{TALKJS_APP_ID}/users/{f_id}"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {TALKJS_SECRET_KEY}"
                }
                payload = {
                    "name": f_id,
                    "role": "default",
                }
                response = requests.put(
                    talkjs_url,
                    json=payload,
                    headers=headers,
                    timeout=5
                )

                talkjs_url = f"https://api.talkjs.com/v1/{TALKJS_APP_ID}/conversations"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {TALKJS_SECRET_KEY}"
                }
                payload = {
                    "participants": [current_user_id, f_id],
                }
                response = requests.put(
                    f"{talkjs_url}/{new_uuid}",
                    json=payload,
                    headers=headers,
                    timeout=5
                )

                if response.status_code == 200:
                    new_entry = Conversation(
                        id=new_uuid, 
                        user_one=current_user_id, 
                        user_two=f_id
                    )
                    db.session.add(new_entry)
                    results[f_id] = new_uuid
                else:
                    results[f_id] = None
                    
            except Exception as e:
                print(f"TalkJS Sync Error for {f_id}: {e}")
                results[f_id] = None

    db.session.commit()
    return jsonify(results), 200
