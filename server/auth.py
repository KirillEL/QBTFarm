from functools import wraps
from flask import request, Response
import os
from server import reloader


def authenticate():
    return Response(
        'Could not verify your access level for that URL. '
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        server_login, server_password = os.getenv('SERVER_LOGIN'), os.getenv('SERVER_PASSWORD')
        if auth is None or (auth.password != server_password or auth.username != server_login):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def api_auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        config = reloader.get_config()
        if config['ENABLE_API_AUTH']:
            if request.headers.get('X-Token', '') != config['API_TOKEN']:
                return Response('Provided token is invalid.', 403)
        return f(*args, **kwargs)
    return decorated

