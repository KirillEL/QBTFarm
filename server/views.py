import re
import time
from datetime import datetime

from flask import jsonify, render_template, request

from server import app, auth, database, reloader
from server.database import db_cursor
from server.models import FlagStatus


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)


@app.route('/')
@auth.auth_required
def index():
    distinct_values = {}
    for column in ['sploit', 'status', 'team']:
        with db_cursor() as (conn, curs):
            curs.execute('SELECT DISTINCT {} FROM flags ORDER BY {}'.format(column, column))
            rows = curs.fetchall()
        distinct_values[column] = [item[column] for item in rows]

    config = reloader.get_config()

    server_tz_name = time.strftime('%Z')
    if server_tz_name.startswith('+'):
        server_tz_name = 'UTC' + server_tz_name

    return render_template('index.html',
                           flag_format=config['FLAG_FORMAT'],
                           distinct_values=distinct_values,
                           server_tz_name=server_tz_name)


FORM_DATETIME_FORMAT = '%Y-%m-%d %H:%M'
FLAGS_PER_PAGE = 30


@app.route('/ui/get_info', methods=['GET'])
def get_info():
    query_1 = 'SELECT Time from flags ORDER BY flags.Time'
    with db_cursor() as (conn, curs):
        curs.execute(query_1)
        sql_time_info = curs.fetchall()
    all_times = []
    flags = []
    for item in sql_time_info:
        
        dt = datetime.fromtimestamp(item[0])
        t = dt.strftime('%Y-%m-%d %H:%M:%S')
        all_times.append(t)
        

    uniq_times = list(set(all_times))
    uniq_times.sort()
    for item in uniq_times:
        query_2 = 'SELECT COUNT(*) FROM flags where flags.status="ACCEPTED" and flags.Time="{}" ORDER BY flags.Time'.format(time.mktime(time.strptime(item, '%Y-%m-%d %H:%M:%S')))
        with db_cursor() as (conn, curs):
            curs.execute(query_2)
            count_flags_for_time = curs.fetchall()
        
        for i in count_flags_for_time:
            flags.append(i[0])
    
    return jsonify({
        'time': uniq_times,
        'flags': flags
    })


@app.route('/ui/show_flags', methods=['POST'])
@auth.auth_required
def show_flags():
    conditions = []
    for column in ['sploit', 'status', 'team']:
        value = request.form[column]
        if value:
            conditions.append((f'{column} = %s', value))
    for column in ['flag', 'checksystem_response']:
        value = request.form[column]
        if value:
            conditions.append((f'POSITION(%s in LOWER({column})) > 0', value.lower()))
    for param in ['time-since', 'time-until']:
        value = request.form[param].strip()
        if value:
            timestamp = round(datetime.strptime(value, FORM_DATETIME_FORMAT).timestamp())
            sign = '>=' if param == 'time-since' else '<='
            conditions.append((f'time {sign} %s', timestamp))
    page_number = int(request.form['page-number'])
    if page_number < 1:
        raise ValueError('Invalid page-number')

    if conditions:
        chunks, values = list(zip(*conditions))
        conditions_sql = 'WHERE ' + ' AND '.join(chunks)
        conditions_args = list(values)
    else:
        conditions_sql = ''
        conditions_args = []

    sql = 'SELECT * FROM flags ' + conditions_sql + ' ORDER BY time DESC LIMIT %s OFFSET %s'
    args = conditions_args + [FLAGS_PER_PAGE, FLAGS_PER_PAGE * (page_number - 1)]
    with db_cursor() as (conn, curs):
        curs.execute(sql, args)
        flags = curs.fetchall()

    sql = 'SELECT COUNT(*) FROM flags ' + conditions_sql
    args = conditions_args
    with db_cursor() as (conn, curs):
        curs.execute(sql, args)
        total_count = curs.fetchone()['count']

    sql_accepted = 'SELECT COUNT(*) FROM flags where flags.status=%s'
    with db_cursor() as (conn, curs):
        curs.execute(sql_accepted, ('ACCEPTED',))
        total_accepted_count = curs.fetchone()['count']
    
    sql_skipped = 'SELECT COUNT(*) FROM flags where flags.status=%s OR flags.status=%s'
    with db_cursor() as (conn, curs):
        curs.execute(sql_skipped, ('QUEUED', 'SKIPPED',))
        total_skipped_count = curs.fetchone()['count']
    
    return jsonify({
        'rows': [dict(item) for item in flags],

        'rows_per_page': FLAGS_PER_PAGE,
        'total_count': total_count,
        'total_accepted_count': total_accepted_count,
        'total_skipped_count': total_skipped_count
    })



@app.route('/ui/post_flags_manual', methods=['POST'])
@auth.auth_required
def post_flags_manual():
    config = reloader.get_config()
    flags = re.findall(config['FLAG_FORMAT'], request.form['text'])

    cur_time = round(time.time())
    rows = [(item, 'Manual', '*', cur_time, FlagStatus.QUEUED.name)
            for item in flags]

    with db_cursor() as (conn, curs):
        for row in rows:
            curs.execute("""
                INSERT INTO flags (flag, sploit, team, time, status)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (flag) DO NOTHING
                """, row)
        conn.commit()

    return ''
