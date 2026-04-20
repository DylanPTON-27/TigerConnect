import sys
import os
from urllib.parse import urlsplit
sys.path.append(os.path.join(os.curdir, "backend"))
import time
from flask import Flask
from flask_cors import CORS
import psycopg as pg
import io
from routes.models import db 
import datetime
import flask_jwt_extended

app = Flask(__name__)
frontend_origin = os.getenv("FRONTEND_ORIGIN")
if not frontend_origin:
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173/app.html")
    parsed = urlsplit(frontend_url)
    frontend_origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme and parsed.netloc else "http://localhost:5173"
CORS(app, origins=[frontend_origin], supports_credentials=True)
basedir = os.path.abspath(os.path.dirname(__file__))

# DB setup
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url or ("sqlite:///" + os.path.join(basedir, "friends.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
db.init_app(app)
with app.app_context():
    db.create_all()


def _pg_conninfo() -> str:
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        # psycopg accepts postgresql:// URLs directly.
        return db_url
    return "dbname=postgres user=postgres password=postgres"

# Friends Route Import
from routes.friends import friends_bp
CORS(friends_bp, origins=[frontend_origin], supports_credentials=True)
app.register_blueprint(friends_bp, url_prefix="/friends")

# Calendar route import
from routes.calendar import calendar_bp
app.register_blueprint(calendar_bp, url_prefix="/calendar")

# Auth setup
app.config["JWT_SECRET_KEY"] = os.getenv("APP_SECRET_KEY", "change-me")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
jwt = flask_jwt_extended.JWTManager(app)

# Auth imports
from routes.auth import auth_bp
app.register_blueprint(auth_bp)
