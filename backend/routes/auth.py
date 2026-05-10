import json
import os
import re
import urllib.parse
import urllib.request

import flask
import flask_jwt_extended
from sqlalchemy.exc import IntegrityError
from .models import db, Users, AuthNonce

auth_bp = flask.Blueprint("auth", __name__)

CAS_URL = os.getenv("CAS_URL", "https://fed.princeton.edu/cas/").rstrip("/") + "/"
IS_DEV = os.getenv("FLASK_ENV", "").lower() == "development"
FRONTEND_URL = os.getenv("FRONTEND_URL") or ("http://localhost:5173/app.html" if IS_DEV else "")
if not FRONTEND_URL:
    raise RuntimeError("FRONTEND_URL must be set in non-development environments.")

def _clean_trailing_punctuation(value: str | None) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip().rstrip(",， ").strip()


def _frontend_landing_url() -> str:
    parsed = urllib.parse.urlsplit(FRONTEND_URL)
    path = parsed.path or "/"
    if path.endswith("/app.html"):
        path = path[: -len("/app.html")] or "/"
    elif path.endswith("app.html"):
        path = path[: -len("app.html")] or "/"
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


def _display_name_from_cas(userinfo: dict, username: str) -> str:
    attributes = (userinfo or {}).get("attributes") or {}
    raw = attributes.get("pudisplayname")
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if isinstance(raw, str):
        value = _clean_trailing_punctuation(raw)
        if value:
            if "," in value:
                last, first = [part.strip() for part in value.split(",", 1)]
                if first and last:
                    return f"{first} {last}"
            return _clean_trailing_punctuation(value)
    if username[0] == ' ':
        username = username[1:]
    return username


def _ensure_user(username: str, display_name: str | None = None) -> Users:
    def _clean_name(value: str | None) -> str | None:
        cleaned = _clean_trailing_punctuation(value)
        return cleaned or None

    user = Users.query.filter_by(netid=username).first()
    if user:
        changed = False
        normalized_existing = _clean_name(user.name)
        normalized_incoming = _clean_name(display_name)

        if normalized_existing != user.name:
            user.name = normalized_existing
            changed = True

        # Only replace name when we have a meaningful incoming display name.
        # Avoid clobbering with placeholder values like raw username/netid.
        if (
            normalized_incoming
            and normalized_incoming.lower() != username.lower()
            and user.name != normalized_incoming
        ):
            user.name = normalized_incoming
            changed = True

        if not user.email:
            user.email = f"{username}@princeton.edu"
            changed = True
        if changed:
            db.session.flush()
        return user

    cleaned_display_name = _clean_name(display_name)
    user = Users(
        netid=username,
        name=cleaned_display_name or username,
        email=f"{username}@princeton.edu",
    )
    db.session.add(user)
    db.session.flush()
    return user


# Helper Functions
def strip_ticket(url):
    if url is None:
        return ""
    url = re.sub(r"ticket=[^&]*&?", "", url)
    url = re.sub(r"\?&?$|&$", "", url)
    return url


def validate(ticket):
    try:
        val_url = (
            CAS_URL
            + "validate"
            + "?service="
            + urllib.parse.quote(strip_ticket(flask.request.url))
            + "&ticket="
            + urllib.parse.quote(ticket)
            + "&format=json"
        )
        with urllib.request.urlopen(val_url, timeout=10) as flo:
            result = json.loads(flo.read().decode("utf-8"))
    except Exception:
        return None

    if (not result) or ("serviceResponse" not in result):
        return None

    sr = result["serviceResponse"]
    if "authenticationSuccess" in sr:
        return sr["authenticationSuccess"]
    return None


# Auth Routes
@auth_bp.route("/login", methods=["GET"])
def login():
    ticket = flask.request.args.get("ticket")

    if ticket is None:
        login_url = CAS_URL + "login?service=" + urllib.parse.quote(flask.request.url)
        return flask.redirect(login_url)

    userinfo = validate(ticket)
    if userinfo is None:
        login_url = CAS_URL + "login?service=" + urllib.parse.quote(strip_ticket(flask.request.url))
        return flask.redirect(login_url)

    username = _clean_trailing_punctuation(str(userinfo.get("user", ""))).lower()
    if not username:
        login_url = CAS_URL + "login?service=" + urllib.parse.quote(strip_ticket(flask.request.url))
        return flask.redirect(login_url)

    real_name = _display_name_from_cas(userinfo, username)
    _ensure_user(username, real_name)

    # nonce to username
    nonce = os.urandom(20).hex()
    db.session.add(AuthNonce(nonce=nonce, username=username))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return flask.jsonify({"error": "failed to initialize login session"}), 500

    return flask.redirect(f"{FRONTEND_URL}?nonce={nonce}")


@auth_bp.route("/api/gettokens", methods=["GET"])
def get_tokens():
    nonce = flask.request.args.get("nonce")
    if nonce is None:
        return flask.jsonify({"error": "missing nonce"}), 400

    row = AuthNonce.query.filter_by(nonce=nonce).first()
    if row is None:
        return flask.jsonify({"error": "invalid nonce"}), 400

    username = row.username
    user = _ensure_user(username, username)
    display_name = _clean_trailing_punctuation(user.name or username)

    db.session.delete(row)
    db.session.commit()

    access_token = flask_jwt_extended.create_access_token(identity=username)
    refresh_token = flask_jwt_extended.create_refresh_token(identity=username)

    return flask.jsonify([username, access_token, refresh_token, display_name])


@auth_bp.route("/api/refreshaccesstoken", methods=["POST"])
@flask_jwt_extended.jwt_required(refresh=True)
def refresh_access_token():
    username = flask_jwt_extended.get_jwt_identity()
    _ensure_user(username, username)
    db.session.commit()
    new_access = flask_jwt_extended.create_access_token(identity=username)
    return flask.jsonify(new_access)


@auth_bp.route("/logoutapp", methods=["GET"])
def logoutapp():
    return flask.redirect(f"{_frontend_landing_url()}?logout=1")
