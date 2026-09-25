# Task and To-Do Management System: OOP vs Imperative Python

A course project for **Programming Languages (CCPGLANG)**. The same task manager
is written twice in Python, once in an **object-oriented** style and once in an
**imperative (procedural)** style. Each version is a complete, independent
system with its own server and front end. A third app shows both side by side.

| App | Folder | Backend | Server | Front end |
|---|---|---|---|---|
| **System A: OOP System** | `system_oop/` | object-oriented Python | Flask, port **5001** | React, port **5173** |
| **System B: Imperative System** | `system_imperative/` | imperative Python | Flask, port **5002** | React, port **5174** |
| **Comparison app** | `system_compare/` | none (uses both servers) | none | React, port **5175** |

```
system_oop/frontend (5173) ───────▶ system_oop/server (5001) ───────▶ system_oop/backend
                                         ▲
system_compare/frontend (5175) ──────────┤
                                         ▼
system_imperative/frontend (5174) ─▶ system_imperative/server (5002) ─▶ system_imperative/backend
```

* **Backends:**
  * `system_oop/backend/`: classes (`Task`, `UrgentTask`, `TaskManager`,
    `JsonTaskStorage`), encapsulation, inheritance, polymorphism, custom
    exceptions.
  * `system_imperative/backend/`: no classes. A `store` dictionary is changed
    step by step by plain procedures, with explicit loops, a recursive merge
    sort and built-in exceptions.
* **Servers:** each `server/app.py` is a thin Flask layer. It reads the
  request, calls one backend function and returns JSON. There is no task
  logic in the servers.
* **Front ends:** React + Vite, and the same design in all three apps. They
  only display data, show forms and call a server. There is no business logic
  in React.
* **Independence:** neither system imports anything from the other. Both
  backends follow the same contract, defined once in
  [`contract/backend_contract.py`](contract/backend_contract.py). Only the
  tests use that file.

## Features

Available in every front end, on both systems:

* Add, view, edit and delete tasks: title, description, due date **and time**,
  priority, status and **category**
* Mark a task as complete
* Search by keyword (title and description)
* Filter by status, priority and/or category
* Sort by due date (date **and** time) or priority, ascending or descending
* Automatic saving after every change, plus manual **Save** / **Load** buttons.
  Each system has its own save file in its `data/` folder, and data is never
  shared between systems.

Business rules (enforced by the backends, never by the UI):

* The title is required (max 100 characters) and the description is at most
  500 characters.
* The **category** is required: `personal`, `academic` or `work`.
* A due date is optional. When given, it must be a real date and time in
  `YYYY-MM-DD HH:MM` form (24-hour). Dates without a time are rejected.
* A **high-priority task must have a due date**.

## Requirements

* Python 3.10 or newer (developed with 3.12)
* Node.js 20.19+ or 22.12+ (needed by Vite 8; developed with Node 24)

The backends and the tests use only the Python standard library. Each server
needs `flask` and `flask-cors` (its `requirements.txt`). Each front end needs
only `react`, `react-dom` and `vite`.

## First-time setup (once per computer)

Open a terminal in the project folder (`PL_FINAL_PROJECT`). One virtual
environment is enough for both servers, because both `requirements.txt` files
are the same.

**1. Create the Python virtual environment.** On Windows:

```bash
python -m venv .venv
```

On macOS / Linux:

```bash
python3 -m venv .venv
```

**2. Install the server packages** (Flask and flask-cors). On Windows:

```bash
.venv\Scripts\python -m pip install -r system_oop\requirements.txt
```

On macOS / Linux:

```bash
.venv/bin/python -m pip install -r system_oop/requirements.txt
```

**3. Install each front end's packages.** Run each of these from the project
folder:

```bash
npm --prefix system_oop/frontend install
```

```bash
npm --prefix system_imperative/frontend install
```

```bash
npm --prefix system_compare/frontend install
```

## How to run

Every server and every front end is a separate program that keeps running, so
**each one needs its own terminal**. In VS Code, open another terminal with the
**+** button in the Terminal panel (or **Ctrl+Shift+`**). Leave the terminals
open while you use the app, and press **Ctrl+C** in a terminal to stop that
program.

Always start a system's **server first**, then its **front end**.

| What | Open the terminal in | Command (Windows) | Then open |
|---|---|---|---|
| OOP server | `PL_FINAL_PROJECT` | `.venv\Scripts\python system_oop\server\app.py` | (port 5001) |
| OOP front end | `PL_FINAL_PROJECT\system_oop\frontend` | `npm run dev` | http://localhost:5173 |
| Imperative server | `PL_FINAL_PROJECT` | `.venv\Scripts\python system_imperative\server\app.py` | (port 5002) |
| Imperative front end | `PL_FINAL_PROJECT\system_imperative\frontend` | `npm run dev` | http://localhost:5174 |
| Comparison app | `PL_FINAL_PROJECT\system_compare\frontend` | `npm run dev` | http://localhost:5175 |

On macOS / Linux, start the servers with `.venv/bin/python` and forward
slashes, e.g. `.venv/bin/python system_oop/server/app.py`.

### Run System A: OOP System

**Terminal 1: server (port 5001).** From the project folder:

```bash
.venv\Scripts\python system_oop\server\app.py
```

It prints `Running on http://127.0.0.1:5001` and keeps running.

**Terminal 2: front end (port 5173).** Go into the front end folder, then start it:

```bash
cd system_oop\frontend
```

```bash
npm run dev
```

When it shows `➜ Local: http://localhost:5173/`, open **http://localhost:5173**.

### Run System B: Imperative System

**Terminal 1: server (port 5002).** From the project folder:

```bash
.venv\Scripts\python system_imperative\server\app.py
```

**Terminal 2: front end (port 5174).** Go into the front end folder, then start it:

```bash
cd system_imperative\frontend
```

```bash
npm run dev
```

When it shows `➜ Local: http://localhost:5174/`, open **http://localhost:5174**.

Both systems can run at the same time (four terminals). They never share data:
each system has its own save file in its `data/` folder.

### Run the comparison app

**Start both servers first** (the OOP server and the Imperative server, see
above). The two system front ends do not need to be running. Then, in a new
terminal:

```bash
cd system_compare\frontend
```

```bash
npm run dev
```

When it shows `➜ Local: http://localhost:5175/`, open **http://localhost:5175**.

* **Normal mode:** use the **OOP System / Imperative System** switch to show
  one system full width. The header shows which system is active and its
  server port.
* **Compare mode:** turn on **Compare** to split the screen: OOP on the left
  (port 5001) and Imperative on the right (port 5002).
  * The shared form **adds** each new task to both systems.
  * The shared toolbar (search, filter, sort, Save, Load) acts on both
    systems.
  * **Edit / Complete / Delete** are on each task inside a half, and only
    affect that system. The same task can have a different id in each system.
  * Errors appear in the half they belong to. If one server is not running,
    that half shows "Cannot connect to the server on port 500X" and the other
    half keeps working.

### If something doesn't work

| What you see | Why | Fix |
|---|---|---|
| Browser: **"This site can't be reached"** / `ERR_CONNECTION_REFUSED` | That front end is not running. | Start it with `npm run dev` in its `frontend` folder, then reload the page. Check the port: OOP 5173, Imperative 5174, comparison 5175. |
| Page loads, but shows **"Cannot connect to the server on port 500X"** | That system's server is not running. | Start the server (5001 = OOP, 5002 = Imperative), then click **Retry**. |
| Terminal: **"Port 517X is already in use"** | That front end is already running in another terminal. | Use the one that is already running, or press Ctrl+C in the other terminal first. |
| Terminal: **`No module named 'flask'`** | The server was started without the virtual environment. | Start it with `.venv\Scripts\python ...` from the project folder, as shown above. |
| Server stops at start-up with **"Could not start"** | Its save file `system_*/data/tasks.json` is unreadable. The server stops on purpose so the file is never overwritten. | Fix or delete that file, then start the server again. |

## Running the tests

No virtual environment is needed; the tests use only the standard library.
From the project root:

```bash
python -m unittest discover tests
```

What runs (220 tests):

| File | What it checks |
|---|---|
| `tests/shared_cases.py` | 100 test cases (normal and error cases) written **once**, including category and date-and-time cases |
| `tests/test_oop.py` | runs those 100 cases on `system_oop/backend`, plus 6 OOP-only checks (inheritance, read-only properties, `due_datetime`, custom exceptions) |
| `tests/test_imperative.py` | runs the same 100 cases on `system_imperative/backend`, plus 3 imperative-only checks (merge sort, built-in exceptions) |
| `tests/test_contract.py` | both backends have every contract function with exactly the same parameters |
| `tests/test_parity.py` | one scripted sequence of 48 calls gives identical results and error messages on both backends |
| `tests/test_frontends_match.py` | the two system front ends are identical apart from the system name, server URL and port; the comparison app uses the same components and styles |
| `tests/test_systems_independent.py` | the two servers are identical apart from name and ports; the comparison app has no backend; no app imports another app or the contract |

The tests call the backends directly (not through the servers) and use
temporary save files, so they never touch the `data/` folders.

## Server API reference

Both servers have exactly the same routes:

* System A: `http://127.0.0.1:5001`
* System B: `http://127.0.0.1:5002`

| Method | URL | Backend function | Success |
|---|---|---|---|
| GET | `/api/health` | none | 200 |
| GET | `/api/options` | `get_options()` | 200 |
| GET | `/api/tasks?keyword=&status=&priority=&category=&sort_by=&descending=` | `query_tasks(...)` | 200 |
| GET | `/api/tasks/<id>` | `get_task(id)` | 200 |
| POST | `/api/tasks` (JSON body) | `add_task(body)` | 201 |
| PUT | `/api/tasks/<id>` (JSON body) | `update_task(id, body)` | 200 |
| PATCH | `/api/tasks/<id>/complete` | `complete_task(id)` | 200 |
| DELETE | `/api/tasks/<id>` | `delete_task(id)` | 200 |
| POST | `/api/save` | `save_tasks()` | 200 |
| POST | `/api/load` | `load_tasks()` | 200 |

A task looks like this (`due_date` is `""` when there is none):

```json
{"id": 1, "title": "Write lab report", "description": "", "due_date": "2026-10-05 14:30",
 "priority": "medium", "status": "pending", "category": "academic"}
```

Errors are returned as `{"error": "<message>"}` with:

| Backend raises | HTTP status |
|---|---|
| `ValueError` (invalid input; OOP: `TaskValidationError`) | 400 |
| `KeyError` (task not found; OOP: `TaskNotFoundError`) | 404 |
| `OSError` (save file problem; OOP: `TaskStorageError`) | 500 |

The front ends use a date-and-time picker. `src/api.js` converts its value
(`YYYY-MM-DDTHH:MM`) to and from the backend format (`YYYY-MM-DD HH:MM`).

## Project structure

```
contract/
  backend_contract.py          the shared function list, task format, rules, errors (tests only)

system_oop/                    System A: OOP System
  backend/                       object-oriented backend
    service.py                     public contract functions (delegate to TaskManager)
    task.py                        Task, UrgentTask, create_task
    task_manager.py                TaskManager
    storage.py                     JsonTaskStorage
    exceptions.py                  custom exception classes
    constants.py
  server/app.py                  Flask server, port 5001
  frontend/                      React app, port 5173
    src/api.js                     server URL + system name (the only differing lines)
    src/App.jsx, main.jsx, labels.js, styles.css
    src/components/                TaskForm, Toolbar, TaskList, TaskItem, MessageBanner
  data/                          tasks.json at runtime (not committed)
  requirements.txt

system_imperative/             System B: Imperative System (same layout)
  backend/                       imperative backend
    service.py                     public contract functions + the `store` dict
    task_ops.py                    add / update / complete / delete procedures
    query_ops.py                   search / filter / recursive merge sort
    validation.py                  validation procedures
    storage.py                     JSON save / load procedures
    constants.py
  server/app.py                  Flask server, port 5002
  frontend/                      React app, port 5174 (same files as System A's)
  data/
  requirements.txt

system_compare/                Comparison app (front end only, no backend)
  frontend/                      React app, port 5175
    src/api.js                     both servers' URLs; one client per server
    src/useSystem.js               state for one system (used once per system)
    src/App.jsx                    normal mode and compare mode
    src/compare.css                layout for the switch and the two halves
    src/components/                ModeSwitch, SystemHalf + the shared components

tests/                         unittest suite (see above)
docs/
  requirements_mapping.md        where each required construct appears in each backend
  comparison_notes.md            architecture and a factual comparison of the two backends
  count_lines.py                 lines-of-code counter used in the comparison
```

## Documentation

* [`docs/requirements_mapping.md`](docs/requirements_mapping.md): for each of
  the 10 required constructs and each paradigm feature, the file and
  function/class where it appears in each backend.
* [`docs/comparison_notes.md`](docs/comparison_notes.md): the architecture,
  then syntax, data types, control structures, subprograms, error handling,
  readability, maintainability, code size, and the comparison app.

To update the line counts after changing a backend:

```bash
python docs/count_lines.py
```
