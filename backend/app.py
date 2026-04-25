import sys
import os
from urllib.parse import urlsplit
sys.path.append(os.path.join(os.curdir, "backend"))
from flask import Flask
from flask_cors import CORS
from routes.models import db 
import datetime
import flask_jwt_extended

app = Flask(__name__)
is_dev = os.getenv("FLASK_ENV", "").lower() == "development"
frontend_origin = os.getenv("FRONTEND_ORIGIN")
if not frontend_origin:
    frontend_url = os.getenv("FRONTEND_URL") or ("http://localhost:5173/app.html" if is_dev else "")
    if not frontend_url:
        raise RuntimeError("Set FRONTEND_ORIGIN or FRONTEND_URL in non-development environments.")
    parsed = urlsplit(frontend_url)
    if not (parsed.scheme and parsed.netloc):
        raise RuntimeError("FRONTEND_URL must be an absolute URL, e.g. https://app.example.com/app.html")
    frontend_origin = f"{parsed.scheme}://{parsed.netloc}"
CORS(app, origins=[frontend_origin], supports_credentials=True)
basedir = os.path.abspath(os.path.dirname(__file__))

# DB setup
db_url = os.getenv("DATABASE_URL")
if not is_dev and not db_url:
    raise RuntimeError("DATABASE_URL must be set in non-development environments.")
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
jwt_secret = os.getenv("APP_SECRET_KEY")
if not is_dev and not jwt_secret:
    raise RuntimeError("APP_SECRET_KEY must be set in non-development environments.")
app.config["JWT_SECRET_KEY"] = jwt_secret or "change-me"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = datetime.timedelta(days=1)
jwt = flask_jwt_extended.JWTManager(app)

# Auth imports
from routes.auth import auth_bp
app.register_blueprint(auth_bp)
