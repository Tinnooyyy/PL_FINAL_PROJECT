"""
The web API that connects the React front end to one of the two backends.

Every route does the same three things:
  1. read the request (URL, query string, JSON body),
  2. call ONE function of the backend chosen with ?backend=oop|imperative,
  3. return the result as JSON (or the error message with a status code).

It deliberately contains no task logic, so the two backends can be compared
fairly.

Start it from the project root with:  python api/app.py
"""

import sys

from flask import Flask, jsonify, request
from flask_cors import CORS

from backend_registry import (
    BACKENDS,
    DATA_FILES,
    configure_all_backends,
    get_backend,
    status_code_for,
)

app = Flask(__name__)

# Keep the key order the backends use (id, title, ...) instead of sorting A-Z.
app.json.sort_keys = False

# Allow the React dev server (a different port) to call this API, and let it
# read the X-Backend header that says which backend answered.
CORS(app, expose_headers=["X-Backend"])


# ----- Helpers ---------------------------------------------------------------

def error_response(message, status_code, backend_name=None):
    """Build a JSON error response like {"error": "Title is required"}."""
    response = jsonify({"error": message})
    response.status_code = status_code
    if backend_name:
        response.headers["X-Backend"] = backend_name
    return response


def call_backend(function_name, *args, success_status=200):
    """Call function_name(*args) on the backend named in ?backend=... and return JSON."""
    backend_name = request.args.get("backend", "")
    backend = get_backend(backend_name)
    if backend is None:
        return error_response(
            f"Unknown backend '{backend_name}'. Use one of: " + ", ".join(BACKENDS), 400)

    try:
        result = getattr(backend, function_name)(*args)
    except (ValueError, KeyError, OSError) as error:
        message = error.args[0] if error.args else str(error)
        return error_response(message, status_code_for(error), backend_name)

    response = jsonify(result)
    response.status_code = success_status
    response.headers["X-Backend"] = backend_name
    return response


# ----- Routes ----------------------------------------------------------------

@app.get("/api/health")
def health():
    """Lets you check that the API is running."""
    return jsonify({"status": "ok", "backends": list(BACKENDS)})


@app.get("/api/options")
def get_options():
    """Allowed priorities, statuses and sort fields."""
    return call_backend("get_options")


@app.get("/api/tasks")
def query_tasks():
    """All tasks, optionally searched, filtered and sorted via the query string."""
    return call_backend(
        "query_tasks",
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
    return call_backend("get_task", task_id)


@app.post("/api/tasks")
def add_task():
    """Create a task from the JSON body."""
    # silent=True gives None for a missing or broken body; the backend then
    # reports the problem with its own error message.
    return call_backend("add_task", request.get_json(silent=True), success_status=201)


@app.put("/api/tasks/<int:task_id>")
def update_task(task_id):
    """Change a task using the fields in the JSON body."""
    return call_backend("update_task", task_id, request.get_json(silent=True))


@app.patch("/api/tasks/<int:task_id>/complete")
def complete_task(task_id):
    """Mark a task as completed."""
    return call_backend("complete_task", task_id)


@app.delete("/api/tasks/<int:task_id>")
def delete_task(task_id):
    """Delete a task."""
    return call_backend("delete_task", task_id)


@app.post("/api/save")
def save_tasks():
    """Write the chosen backend's tasks to its save file."""
    return call_backend("save_tasks")


@app.post("/api/load")
def load_tasks():
    """Reload the chosen backend's tasks from its save file."""
    return call_backend("load_tasks")


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
    """Load both backends' save files, then start the development server."""
    try:
        loaded = configure_all_backends()
    except OSError as error:
        # Stop instead of starting empty: an empty backend would auto-save
        # over the unreadable file and its data would be lost.
        print(f"Could not start: {error}", file=sys.stderr)
        print("Fix or delete the file in the data/ folder, then start again.",
              file=sys.stderr)
        sys.exit(1)

    for name, result in loaded.items():
        print(f"[{name}] loaded {result['loaded']} task(s) from {DATA_FILES[name]}")
    app.run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
