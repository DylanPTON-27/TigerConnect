import os
import re
import json
import urllib.parse
import urllib.request
import flask
import flask_jwt_extended

from models import db, User, AuthNonce

auth_bp = flask.Blueprint("auth", __name__)

CAS_URL = os.getenv("CAS_URL", "https://fed.princeton.edu/cas/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Helper Functions
def strip_ticket(url):
    if url is None:
        return ""
    url = re.sub(r"ticket=[^&]*&?", "", url)
    url = re.sub(r"\?&?$|&$", "", url)
    return url


def validate(ticket):
    val_url = (
        CAS_URL + "validate"
        + "?service=" + urllib.parse.quote(strip_ticket(flask.request.url))
        + "&ticket=" + urllib.parse.quote(ticket)
        + "&format=json"
    )
    with urllib.request.urlopen(val_url) as flo:
        result = json.loads(flo.read().decode("utf-8"))

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

    username = userinfo["user"].strip().lower()

    # ensure user exists
    user = User.query.filter_by(netid=username).first()
    if not user:
        db.session.add(User(netid=username, name=username, email=f"{username}@princeton.edu"))

    # nonce to username
    nonce = os.urandom(20).hex()
    db.session.add(AuthNonce(nonce=nonce, username=username))
    db.session.commit()

    return flask.redirect(f"{FRONTEND_URL}/?nonce={nonce}")


@auth_bp.route("/api/gettokens", methods=["GET"])
def get_tokens():
    nonce = flask.request.args.get("nonce")
    if nonce is None:
        return flask.jsonify({"error": "missing nonce"}), 400

    row = AuthNonce.query.filter_by(nonce=nonce).first()
    if row is None:
        return flask.jsonify({"error": "invalid nonce"}), 400

    username = row.username
    db.session.delete(row)
    db.session.commit()

    access_token = flask_jwt_extended.create_access_token(identity=username)
    refresh_token = flask_jwt_extended.create_refresh_token(identity=username)

    return flask.jsonify([username, access_token, refresh_token])


@auth_bp.route("/api/refreshaccesstoken", methods=["POST"])
@flask_jwt_extended.jwt_required(refresh=True)
def refresh_access_token():
    username = flask_jwt_extended.get_jwt_identity()
    new_access = flask_jwt_extended.create_access_token(identity=username)
    return flask.jsonify(new_access)

@auth_bp.route("/logoutapp", methods=["GET"])
def logoutapp():
    return flask.redirect(f"{FRONTEND_URL}/logout")