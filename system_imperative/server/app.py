"""
The web server of the Imperative System.

Every route does the same three things:
  1. read the request (URL, query string, JSON body),
  2. call ONE function of this system's backend (backend/service.py),
  3. return the result as JSON, or the error message with a status code.

It deliberately contains no task logic, so the backends of the two systems
can be compared fairly.

Start it from the project root with:   python system_imperative/server/app.py
or from inside the system_imperative folder:  python server/app.py
"""

import os
import sys

from flask import Flask, jsonify, request
from flask_cors import CORS

# The system_imperative folder. Putting it on the import path lets us import this
# system's own `backend` package, and nothing from any other system.
SYSTEM_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SYSTEM_DIR not in sys.path:
    sys.path.insert(0, SYSTEM_DIR)

from backend import service  # noqa: E402

SYSTEM_NAME = "Imperative System"
PORT = 5002
FRONTEND_PORT = 5174
COMPARE_APP_PORT = 5175  # system_compare: the app that shows both systems
DATA_FILE = os.path.join(SYSTEM_DIR, "data", "tasks.json")

app = Flask(__name__)

# Keep the key order the backend uses (id, title, ...) instead of sorting A-Z.
app.json.sort_keys = False

# Only this system's own front end and the comparison app may call this
# server from a browser.
CORS(app, origins=[f"http://localhost:{FRONTEND_PORT}",
                   f"http://127.0.0.1:{FRONTEND_PORT}",
                   f"http://localhost:{COMPARE_APP_PORT}",
                   f"http://127.0.0.1:{COMPARE_APP_PORT}"])


# ----- Helpers ---------------------------------------------------------------

def status_code_for(error):
    """
    Map a backend error to an HTTP status code.

    The backend raises (subclasses of) these three built-in types; see
    contract/backend_contract.py.
    """
    if isinstance(error, KeyError):
        return 404  # task not found
    if isinstance(error, ValueError):
        return 400  # invalid input
    return 500      # OSError: the save file could not be read or written


def error_response(message, status_code):
    """Build a JSON error response like {"error": "Title is required"}."""
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


def respond(backend_function, *args, success_status=200):
    """Call backend_function(*args) and turn the result (or error) into JSON."""
    try:
        result = backend_function(*args)
    except (ValueError, KeyError, OSError) as error:
        message = error.args[0] if error.args else str(error)
        return error_response(message, status_code_for(error))

    response = jsonify(result)
    response.status_code = success_status
    return response


# ----- Routes ----------------------------------------------------------------

@app.get("/api/health")
def health():
    """Lets you check that the server is running."""
    return jsonify({"status": "ok", "system": SYSTEM_NAME})


@app.get("/api/options")
def get_options():
    """Allowed priorities, statuses, categories and sort fields."""
    return respond(service.get_options)


@app.get("/api/tasks")
def query_tasks():
    """All tasks, optionally searched, filtered and sorted via the query string."""
    return respond(
        service.query_tasks,
        request.args.get("keyword"),
        request.args.get("status"),
        request.args.get("priority"),
        request.args.get("category"),
        request.args.get("sort_by"),
        request.args.get("descending", False),
    )


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id):
    """One task."""
    return respond(service.get_task, task_id)


@app.post("/api/tasks")
def add_task():
    """Create a task from the JSON body."""
    # silent=True gives None for a missing or broken body; the backend then
    # reports the problem with its own error message.
    return respond(service.add_task, request.get_json(silent=True), success_status=201)


@app.put("/api/tasks/<int:task_id>")
def update_task(task_id):
    """Change a task using the fields in the JSON body."""
    return respond(service.update_task, task_id, request.get_json(silent=True))


@app.patch("/api/tasks/<int:task_id>/complete")
def complete_task(task_id):
    """Mark a task as completed."""
    return respond(service.complete_task, task_id)


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    """Delete a task."""
    return respond(service.delete_task, task_id)


@app.post("/api/save")
def save_tasks():
    """Write the tasks to the save file."""
    return respond(service.save_tasks)


@app.post("/api/load")
def load_tasks():
    """Reload the tasks from the save file."""
    return respond(service.load_tasks)


# ----- JSON versions of Flask's built-in errors --------------------------------

@app.errorhandler(404)
def not_found(_error):
    """Unknown URL."""
    return error_response(f"Not found: {request.path}", 404)


@app.errorhandler(405)
def method_not_allowed(_error):
    """Known URL, wrong HTTP method."""
    return error_response(f"Method {request.method} is not allowed for {request.path}", 405)


@app.errorhandler(500)
def internal_error(_error):
    """Anything unexpected."""
    return error_response("Internal server error", 500)


# ----- Start-up --------------------------------------------------------------

def main():
    """Load the save file, then start the development server."""
    try:
        loaded = service.configure(DATA_FILE)
    except OSError as error:
        # Stop instead of starting empty: an empty backend would auto-save
        # over the unreadable file and its data would be lost.
        print(f"Could not start: {error}", file=sys.stderr)
        print(f"Fix or delete {DATA_FILE}, then start again.", file=sys.stderr)
        sys.exit(1)

    print(f"[{SYSTEM_NAME}] loaded {loaded['loaded']} task(s) from {DATA_FILE}")
    print(f"[{SYSTEM_NAME}] front end allowed from port {FRONTEND_PORT}")
    app.run(host="127.0.0.1", port=PORT)


if __name__ == "__main__":
    main()
