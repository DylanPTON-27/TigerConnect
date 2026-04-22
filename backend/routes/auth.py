import json
import os
import re
import urllib.parse
import urllib.request

import flask
import flask_jwt_extended
from .models import db, Users, AuthNonce

auth_bp = flask.Blueprint("auth", __name__)

CAS_URL = os.getenv("CAS_URL", "https://fed.princeton.edu/cas/")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173/app.html")


def _frontend_landing_url() -> str:
    parsed = urllib.parse.urlsplit(FRONTEND_URL)
    path = parsed.path or "/"
    if path.endswith("/app.html"):
        path = path[: -len("/app.html")] or "/"
    elif path.endswith("app.html"):
        path = path[: -len("app.html")] or "/"
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))


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

    username = userinfo["user"].strip().lower()
    real_name = userinfo["attributes"]["pudisplayname"][0]
    real_name = real_name.split(", ")
    real_name = f"{real_name[1]} {real_name[0]}"

    # ensure user exists
    user = Users.query.filter_by(netid=username).first()
    if not user:
        db.session.add(Users(netid=username, name=real_name, email=f"{username}@princeton.edu"))
        db.session.flush()

    # nonce to username
    nonce = os.urandom(20).hex()
    db.session.add(AuthNonce(nonce=nonce, username=username))
    db.session.commit()

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
    
    display_name = Users.query.filter_by(netid=username).first().name
    print(display_name)

    db.session.delete(row)
    db.session.commit()

    access_token = flask_jwt_extended.create_access_token(identity=username)
    refresh_token = flask_jwt_extended.create_refresh_token(identity=username)

    return flask.jsonify([username, access_token, refresh_token, display_name])


@auth_bp.route("/api/refreshaccesstoken", methods=["POST"])
@flask_jwt_extended.jwt_required(refresh=True)
def refresh_access_token():
    username = flask_jwt_extended.get_jwt_identity()
    new_access = flask_jwt_extended.create_access_token(identity=username)
    return flask.jsonify(new_access)


@auth_bp.route("/logoutapp", methods=["GET"])
def logoutapp():
    return flask.redirect(f"{_frontend_landing_url()}?logout=1")
