# Task and To-Do Management System: OOP vs Imperative Python

A course project for **Programming Languages (CCPGLANG)**. The same task manager
is written twice in Python, once in an **object-oriented** style and once in an
**imperative (procedural)** style, and both are driven by one shared React front
end so they can be compared side by side.

```
React front end  ──HTTP──▶  Flask API  ──?backend=oop─────────▶  backend_oop/
 (frontend/)                 (api/)    ──?backend=imperative──▶  backend_imperative/
```

* **`backend_oop/`**: classes (`Task`, `UrgentTask`, `TaskManager`,
  `JsonTaskStorage`), encapsulation, inheritance, polymorphism, custom exceptions.
* **`backend_imperative/`**: no classes; a `store` dictionary changed step by
  step by plain procedures, with explicit loops, a recursive merge sort and
  built-in exceptions.
* **`api/`**: a thin Flask layer. It only reads the request, calls one backend
  function and returns JSON. It contains no task logic.
* **`frontend/`**: React + Vite. It only displays data, shows forms and calls
  the API. It contains no business logic.

Both backends expose exactly the same functions, defined once in
[`contract/backend_contract.py`](contract/backend_contract.py).

## Features

Available from the UI on both backends:

* Add, view, edit and delete tasks (title, description, due date, priority, status)
* Mark a task as complete
* Search by keyword (title and description)
* Filter by status and/or priority
* Sort by due date or priority, ascending or descending
* Automatic saving after every change, plus manual **Save** / **Load** buttons.
  Each backend has its own file: `data/tasks_oop.json` and
  `data/tasks_imperative.json`.

Business rules (enforced by the backends, never by the UI): the title is
required (max 100 characters), the description is at most 500 characters,
dates must be real `YYYY-MM-DD` dates, and a **high-priority task must have a
due date**.

## Requirements

* Python 3.10 or newer (developed with 3.12)
* Node.js 20.19+ or 22.12+ (needed by Vite 8; developed with Node 24)

The two backends and the tests use only the Python standard library. The API
needs `flask` and `flask-cors`. The front end needs only `react`, `react-dom`
and `vite`.

## Setup and running

Open **two terminals** in the project folder.

### Terminal 1: the API

Create a virtual environment and install Flask (first time only).

Windows:

```bash
python -m venv .venv
```

```bash
.venv\Scripts\activate
```

macOS / Linux:

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

Then, on any system:

```bash
pip install -r requirements.txt
```

Start the API (it runs at `http://127.0.0.1:5000`):

```bash
python api/app.py
```

On start-up it prints how many tasks each backend loaded. If a save file is
unreadable it stops with an error instead of starting empty, so the file is
never overwritten. Fix or delete the file in `data/` and start again.

### Terminal 2: the React app

```bash
cd frontend
```

```bash
npm install
```

```bash
npm run dev
```

Then open **http://localhost:5173** in a browser.

If the API runs somewhere else, set `VITE_API_URL` before `npm run dev`
(default: `http://127.0.0.1:5000/api`).

## Switching backends

Use the **Object-Oriented / Imperative** switch in the top-right corner.

* The top border, buttons and the "Active backend" label change colour:
  indigo for OOP, amber for Imperative.
* "last response from `oop` / `imperative`" shows which backend actually
  answered, taken from the API's `X-Backend` response header.
* Each backend keeps its own tasks. Switching does not copy data between them.

Every request sends `?backend=oop` or `?backend=imperative`, and the API passes
it to that backend.

## Running the tests

No virtual environment is needed; the tests use only the standard library.
From the project root:

```bash
python -m unittest discover tests
```

What runs (161 tests):

| File | What it checks |
|---|---|
| `tests/shared_cases.py` | 75 test cases (normal and error cases) written **once** |
| `tests/test_oop.py` | runs those 75 cases on the OOP backend, plus 5 OOP-only checks (inheritance, read-only properties, custom exceptions) |
| `tests/test_imperative.py` | runs the same 75 cases on the imperative backend, plus 3 imperative-only checks (merge sort, built-in exceptions) |
| `tests/test_contract.py` | both backends have every contract function with exactly the same parameters |
| `tests/test_parity.py` | one scripted sequence of 35 calls gives identical results and error messages on both backends |

The tests call the backends directly (not through the API) and use temporary
save files, so they never touch `data/`.

## API reference

All task routes need `?backend=oop` or `?backend=imperative`.

| Method | URL | Backend function | Success |
|---|---|---|---|
| GET | `/api/health` | none | 200 |
| GET | `/api/options` | `get_options()` | 200 |
| GET | `/api/tasks?keyword=&status=&priority=&sort_by=&descending=` | `query_tasks(...)` | 200 |
| GET | `/api/tasks/<id>` | `get_task(id)` | 200 |
| POST | `/api/tasks` (JSON body) | `add_task(body)` | 201 |
| PUT | `/api/tasks/<id>` (JSON body) | `update_task(id, body)` | 200 |
| PATCH | `/api/tasks/<id>/complete` | `complete_task(id)` | 200 |
| DELETE | `/api/tasks/<id>` | `delete_task(id)` | 200 |
| POST | `/api/save` | `save_tasks()` | 200 |
| POST | `/api/load` | `load_tasks()` | 200 |

Errors are returned as `{"error": "<message>"}` with:

| Backend raises | HTTP status |
|---|---|
| `ValueError` (invalid input; OOP: `TaskValidationError`) | 400 |
| `KeyError` (task not found; OOP: `TaskNotFoundError`) | 404 |
| `OSError` (save file problem; OOP: `TaskStorageError`) | 500 |
| unknown or missing `backend` | 400 |

## Project structure

```
contract/backend_contract.py   the shared function list, task format, rules, errors
backend_oop/                   object-oriented backend
  service.py                     public contract functions (delegate to TaskManager)
  task.py                        Task, UrgentTask, create_task
  task_manager.py                TaskManager
  storage.py                     JsonTaskStorage
  exceptions.py                  custom exception classes
  constants.py
backend_imperative/            imperative backend
  service.py                     public contract functions + the `store` dict
  task_ops.py                    add / update / complete / delete procedures
  query_ops.py                   search / filter / recursive merge sort
  validation.py                  validation procedures
  storage.py                     JSON save / load procedures
  constants.py
api/
  app.py                         Flask routes
  backend_registry.py            backend names, data files, error → status code
frontend/src/
  App.jsx                        state and API calls
  api.js                         fetch wrapper
  components/                    BackendToggle, TaskForm, Toolbar, TaskList, TaskItem, MessageBanner
tests/                         unittest suite (see above)
data/                          runtime save files (not committed)
docs/
  requirements_mapping.md        where each required construct appears in each backend
  comparison_notes.md            factual comparison of the two backends
  count_lines.py                 lines-of-code counter used in the comparison
```

## Documentation

* [`docs/requirements_mapping.md`](docs/requirements_mapping.md): for each of
  the 10 required constructs and each paradigm feature, the file and
  function/class where it appears in each backend.
* [`docs/comparison_notes.md`](docs/comparison_notes.md): syntax, data types,
  control structures, subprograms, error handling, readability,
  maintainability and code size.

To update the line counts after changing a backend:

```bash
python docs/count_lines.py
```
