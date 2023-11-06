import re
import time
from datetime import datetime

from flask import jsonify, render_template, request

from server import app, auth, database, reloader
from server.models import FlagStatus


@app.template_filter('timestamp_to_datetime')
def timestamp_to_datetime(s):
    return datetime.fromtimestamp(s)


@app.route('/')
@auth.auth_required
def index():
    distinct_values = {}
    for column in ['sploit', 'status', 'team']:
        rows = database.query('SELECT DISTINCT {} FROM flags ORDER BY {}'.format(column, column))
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
    sql_time_info = database.query(query_1)
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
        count_flags_for_time = database.query(query_2)
        
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
            conditions.append(('{} = ?'.format(column), value))
    for column in ['flag', 'checksystem_response']:
        value = request.form[column]
        if value:
            conditions.append(('INSTR(LOWER({}), ?)'.format(column), value.lower()))
    for param in ['time-since', 'time-until']:
        value = request.form[param].strip()
        if value:
            timestamp = round(datetime.strptime(value, FORM_DATETIME_FORMAT).timestamp())
            sign = '>=' if param == 'time-since' else '<='
            conditions.append(('time {} ?'.format(sign), timestamp))
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

    sql = 'SELECT * FROM flags ' + conditions_sql + ' ORDER BY time DESC LIMIT ? OFFSET ?'
    args = conditions_args + [FLAGS_PER_PAGE, FLAGS_PER_PAGE * (page_number - 1)]
    flags = database.query(sql, args)

    sql = 'SELECT COUNT(*) FROM flags ' + conditions_sql
    args = conditions_args
    total_count = database.query(sql, args)[0][0]

    sql_accepted = 'SELECT COUNT(*) FROM flags where flags.status="ACCEPTED"'
    total_accepted_count = database.query(sql_accepted)[0][0]
    
    sql_skipped = 'SELECT COUNT(*) FROM flags where flags.status="SKIPPED" OR flags.status="QUEUED"'
    total_skipped_count = database.query(sql_skipped)[0][0]
    
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

    db = database.get()
    db.executemany("INSERT OR IGNORE INTO flags (flag, sploit, team, time, status) "
                   "VALUES (?, ?, ?, ?, ?)", rows)
    db.commit()

    return ''
