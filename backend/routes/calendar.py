import os
import requests
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, redirect, make_response
from .models import db, CalendarAccount, CalendarEvent, Calendar
from flask_jwt_extended import get_jwt_identity, jwt_required, get_jwt
from .friends import get_all_friends
import psycopg as pg
import random

calendar_bp = Blueprint("calendar", __name__)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CAL_EVENTS = "https://www.googleapis.com/calendar/v3/calendars/primary/events"

SCOPES = "https://www.googleapis.com/auth/calendar.readonly"

def utc_dt(iso_str):
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00")).astimezone(timezone.utc)

def _pg_conninfo() -> str:
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # psycopg accepts postgresql:// URLs directly.
        return db_url
    return "dbname=postgres user=postgres password=postgres"

@calendar_bp.route("/auth/start", methods=["GET"])
@jwt_required()
def auth_start():
    user = get_jwt_identity()
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": SCOPES,
        "access_type": "offline",
        "prompt": "consent",
        "state": user,
    }
    q = "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
    return redirect(f"{GOOGLE_AUTH_URL}?{q}")

@calendar_bp.route("/auth/callback", methods=["GET"])
def auth_callback():
    code = request.args.get("code")
    user = request.args.get("state")
    if not code or not user:
        return {"error": "missing code/state"}, 400

    token_resp = requests.post(GOOGLE_TOKEN_URL, data={
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }).json()

    access_token = token_resp["access_token"]
    refresh_token = token_resp.get("refresh_token")
    expires_in = token_resp.get("expires_in", 3600)
    expires_at = datetime.now() + timedelta(seconds=expires_in)

    acct = CalendarAccount.query.filter_by(user_id=user).first()
    if not acct:
        acct = CalendarAccount(user_id=user, provider="google", access_token=access_token,
                               refresh_token=refresh_token, expires_at=expires_at)
        db.session.add(acct)
    else:
        acct.access_token = access_token
        if refresh_token:
            acct.refresh_token = refresh_token
        acct.expires_at = expires_at
    db.session.commit()

    return {"message": "calendar connected"}

def refresh_access_token(acct: CalendarAccount):
    if not acct.refresh_token:
        return False
    token_resp = requests.post(GOOGLE_TOKEN_URL, data={
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "refresh_token": acct.refresh_token,
        "grant_type": "refresh_token"
    }).json()
    acct.access_token = token_resp["access_token"]
    expires_in = token_resp.get("expires_in", 3600)
    acct.expires_at = datetime.now() + timedelta(seconds=expires_in)
    db.session.commit()
    return True

@calendar_bp.route("/sync", methods=["POST"])
@jwt_required()
def sync_calendar():
    user = get_jwt_identity()
    acct = CalendarAccount.query.filter_by(user_id=user).first()
    if not acct:
        return {"error": "calendar not connected"}, 400

    if acct.expires_at and acct.expires_at < datetime.now():
        if not refresh_access_token(acct):
            return {"error": "token expired"}, 401

    now = datetime.now().replace(tzinfo=timezone.utc)
    time_min = now.isoformat()
    time_max = (now + timedelta(days=30)).isoformat()

    headers = {"Authorization": f"Bearer {acct.access_token}"}
    params = {"timeMin": time_min, "timeMax": time_max, "singleEvents": True, "orderBy": "startTime"}
    resp = requests.get(GOOGLE_CAL_EVENTS, headers=headers, params=params)
    if resp.status_code != 200:
        return {"error": "failed to fetch events"}, 400

    items = resp.json().get("items", [])
    for ev in items:
        provider_id = ev["id"]
        title = ev.get("summary", "")
        start_raw = ev["start"].get("dateTime") or ev["start"].get("date")
        end_raw = ev["end"].get("dateTime") or ev["end"].get("date")
        if not start_raw or not end_raw:
            continue

        start_utc = utc_dt(start_raw)
        end_utc = utc_dt(end_raw)

        existing = CalendarEvent.query.filter_by(user_id=user, provider_event_id=provider_id).first()
        if not existing:
            db.session.add(CalendarEvent(
                user_id=user,
                provider_event_id=provider_id,
                title=title,
                start_utc=start_utc.replace(tzinfo=None),
                end_utc=end_utc.replace(tzinfo=None),
                timezone="UTC",
                updated_at=datetime.now()
            ))
        else:
            existing.title = title
            existing.start_utc = start_utc.replace(tzinfo=None)
            existing.end_utc = end_utc.replace(tzinfo=None)
            existing.updated_at = datetime.now()

    db.session.commit()
    return {"message": "synced", "count": len(items)}

def build_busy_blocks(events, window_start, window_end, minutes=30):
    blocks = []
    cur = window_start
    while cur < window_end:
        blocks.append({"start": cur, "end": cur + timedelta(minutes=minutes), "busy": False})
        cur += timedelta(minutes=minutes)

    for ev in events:
        for b in blocks:
            if ev.start_utc < b["end"] and ev.end_utc > b["start"]:
                b["busy"] = True
    return blocks

@calendar_bp.route("/overlay", methods=["POST"])
@jwt_required()
def overlay():
    data = request.json
    users = data["users"]  # list of netids
    window_days = data.get("days", 7)
    minutes = data.get("minutes", 30)

    now = datetime.now()
    window_start = now.replace(minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(days=window_days)

    results = {}
    for u in users:
        events = CalendarEvent.query.filter(
            CalendarEvent.user_id == u,
            CalendarEvent.end_utc > window_start,
            CalendarEvent.start_utc < window_end
        ).all()
        results[u] = [
            {
                "title": e.title,
                "start": e.start_utc.isoformat(),
                "end": e.end_utc.isoformat()
            } for e in events
        ]
    return jsonify(results)

@calendar_bp.route("/suggest", methods=["POST"])
@jwt_required()
def suggest():
    data = request.json
    users = data["users"]
    window_days = data.get("days", 7)
    minutes = data.get("minutes", 30)

    now = datetime.now()
    window_start = now.replace(minute=0, second=0, microsecond=0)
    window_end = window_start + timedelta(days=window_days)

    all_blocks = []
    for u in users:
        events = CalendarEvent.query.filter(
            CalendarEvent.user_id == u,
            CalendarEvent.end_utc > window_start,
            CalendarEvent.start_utc < window_end
        ).all()
        blocks = build_busy_blocks(events, window_start, window_end, minutes)
        all_blocks.append(blocks)

    # Intersections
    suggestions = []
    for i in range(len(all_blocks[0])):
        if all(not blocks[i]["busy"] for blocks in all_blocks):
            suggestions.append({
                "start": all_blocks[0][i]["start"].isoformat(),
                "end": all_blocks[0][i]["end"].isoformat()
            })

    return jsonify({"suggestions": suggestions})

# ------------------------------------------------------------------------------
# .ICS CALENDAR ROUTES
# ------------------------------------------------------------------------------

@calendar_bp.route('/get_cal', methods=['POST'])
@jwt_required()
def get_cal():
    user = get_jwt_identity()
    # Assuming get_all_friends returns a list of strings (NetIDs)
    users_to_fetch = get_all_friends(user)
    users_to_fetch.append(user)
    
    # Query using the IN operator
    rows = Calendar.query.filter(Calendar.uid.in_(users_to_fetch)).all()
    
    if not rows:
        return {"error": "no uploaded calendar found"}, 404
        
    # Combine all ics contents
    combined_content = "".join([row.content for row in rows])
    
    response = make_response(combined_content)
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    return response

def clean_ics(content: str, user: str) -> str:
    new_content = ""
    for line in content.splitlines():
        start = line.split(':')[0]
        if 'BEGIN' in start or 'DT' in start or 'LAST' in start or 'END' in start:
            new_content += line + '\n'
        elif 'SUMMARY' in start:
            new_content += f"SUMMARY:{user}\n"
    return new_content
        

@calendar_bp.route('/upload', methods=['POST'])
@jwt_required()
def receive_cal():
    user = get_jwt_identity()
    file = request.files.get('file')
    
    if not file:
        return {'error': 'missing file'}, 400

    is_ics = file.content_type == 'text/calendar' or file.filename.lower().endswith('.ics')
    
    if is_ics:
        raw_content = file.read().decode('utf-8')
        cleaned_content = clean_ics(raw_content, user)
        
        # Look for existing calendar for this user
        cal = Calendar.query.filter_by(uid=user).first()
        
        if cal:
            # Update existing
            cal.filename = file.filename
            cal.content = cleaned_content
        else:
            # Create new
            new_cal = Calendar(
                uid=user, 
                filename=file.filename, 
                content=cleaned_content
            )
            db.session.add(new_cal)
            
        db.session.commit()
        return 'Received!'
    
    return 'Wrong File Type!', 400
