import sys
import os
sys.path.append(os.path.join(os.curdir, "backend"))
import time
from flask import Flask, make_response, request
from flask_cors import CORS
import psycopg as pg
import io
from models import db 
import datetime
import flask_jwt_extended

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=True)
basedir = os.path.abspath(os.path.dirname(__file__))
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config["SQLALCHEMY_DATABASE_URI"] = db_url or ("sqlite:///" + os.path.join(basedir, "friends.db"))
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False 
db.init_app(app)
# Friends Route Import
from routes.friends import friends_bp
CORS(friends_bp, origins=["http://localhost:5173"], supports_credentials=True)
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

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/api/calendar', methods=['POST'])
def get_cal():
    with pg.connect("dbname=postgres user=postgres password=postgres") as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT filename, content FROM calendars WHERE id = (SELECT MAX(id) FROM calendars);"
            )
            fname, content = cur.fetchone()
    response = make_response(content)
    response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
    return response

@app.route('/api/upload', methods=['POST'])
def receive_cal():
    file = request.files['file']
    if file.content_type == 'text/calendar':
        with pg.connect("dbname=postgres user=postgres password=postgres") as conn:
            with conn.cursor() as cur:
                content = file.read().decode('utf-8')
                cur.execute(
                    "INSERT INTO calendars (filename, content) values (%s, %s)",
                    (file.filename, content)
                )
        return 'Received!'
    else:
        return 'Wrong File Type!'
