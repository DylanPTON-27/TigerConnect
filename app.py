import time
from flask import Flask, make_response, request
import psycopg as pg
import io

app = Flask(__name__)

@app.route('/api/time')
def get_current_time():
    return {'time': time.time()}

@app.route('/api/calendar')
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
