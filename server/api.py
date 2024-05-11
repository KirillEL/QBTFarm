import time

from flask import request, jsonify

from server import app, auth, database, reloader
from server.database import db_cursor
from server.models import FlagStatus
from server.spam import is_spam_flag


@app.route('/api/get_config')
@auth.api_auth_required
def get_config():
    config = reloader.get_config()
    return jsonify({key: value for key, value in config.items()
                    if 'PASSWORD' not in key and 'TOKEN' not in key})


@app.route('/api/post_flags', methods=['POST'])
@auth.api_auth_required
def post_flags():
    flags = request.get_json()
    print(flags)
    flags = [item for item in flags if not is_spam_flag(item['flag'])]

    cur_time = round(time.time())
    rows = [(item['flag'], item['sploit'], item['team'], cur_time, FlagStatus.QUEUED.name)
            for item in flags]

    with db_cursor() as (conn, curs):
        curs.executemany("""
        INSERT INTO flags (flag, sploit, team, time, status) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (flag) DO NOTHING;
        """, rows)
        conn.commit()

    return ''
