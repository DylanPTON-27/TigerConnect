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

@auth_bp.route("/api/gettokens", methods=["GET"])
def get_tokens():  

@auth_bp.route("/api/refreshaccesstoken", methods=["POST"])
@flask_jwt_extended.jwt_required(refresh=True)
def refresh_access_token():

@auth_bp.route("/logoutapp", methods=["GET"])
def logoutapp():
    return flask.redirect(f"{FRONTEND_URL}/logout")