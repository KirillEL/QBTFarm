import threading
import werkzeug.serving

from server import app
import server.submit_loop
from server.submit_loop import run_loop


def start_submit_loop():
    app.logger.info("Starting submit loop thread")
    thread = threading.Thread(target=run_loop, daemon=True)
    thread.start()
    return thread


if not werkzeug.serving.is_running_from_reloader():
    start_submit_loop()
