# Comparison Notes: Object-Oriented vs Imperative Backend

These notes compare the two **backends**: `system_oop/backend/` and
`system_imperative/backend/`. The servers, the React front ends and the
comparison app are described only in the Architecture section and section 9,
because they are deliberately the same for both systems.

Every statement refers to code in this repository. Counts marked *(AST)* were
taken by parsing the source with Python's `ast` module; line counts come from
`python docs/count_lines.py`.

---

## 0. Architecture

```
system_oop/                          system_imperative/
  backend/   OOP backend               backend/   imperative backend
  server/    Flask, port 5001          server/    Flask, port 5002
  frontend/  React, port 5173          frontend/  React, port 5174
  data/      tasks.json                data/      tasks.json

system_compare/
  frontend/  React, port 5175 (no backend; calls both servers)
```

* **Two independent systems.** Each system has its own backend, server, front
  end and save file, and runs on its own. Neither system imports anything from
  the other (checked by `tests/test_systems_independent.py`).
* **Same contract.** Both backends implement the functions in
  [`contract/backend_contract.py`](../contract/backend_contract.py). Only the
  tests use that file; the systems never import it. The tests check that
  both backends:
  * have the same function signatures (`tests/test_contract.py`)
  * pass the same 100 shared test cases (`tests/shared_cases.py`)
  * return identical results and error messages for a 48-step script
    (`tests/test_parity.py`)
* **Same server and front end.** The two `server/app.py` files are identical
  except for the system name, folder and ports. The two `frontend/` folders are
  identical except for the system name and server URL in `src/api.js` and the
  port in `vite.config.js`. `tests/test_systems_independent.py` and
  `tests/test_frontends_match.py` check this. So any difference between the
  two systems comes from the backends.
* **Thin servers.** Each route reads the request, calls one backend function
  and returns JSON. Errors map the same way in both: `ValueError` → 400,
  `KeyError` → 404, `OSError` → 500.
* **Comparison app.** `system_compare/` shows both systems at once (see
  section 9). It has no backend and uses the two servers above.

---

## 1. Syntax

| Aspect | Object-Oriented | Imperative |
|---|---|---|
| Main building block | `class` (8 classes *(AST)*) | `def` at module level (45 functions *(AST)*) |
| Reading a field | attribute access through a property: `task.status` | dictionary subscript: `task["status"]` |
| Reaching shared state | through `self`: `self._tasks`, `self._next_id` | through a parameter: `store["tasks"]`, `store["next_id"]` |
| Decorators | `@property` ×9, `@staticmethod` ×7, `@classmethod` ×1 | none |
| Calling the parent version | `super().validate()` in `UrgentTask.validate`; `super().__init__(message)` in `TaskError.__init__` | not applicable |
| Building messages | f-strings (14 *(AST)*), e.g. `f"Task {self._id} is already completed"` | `+` and `str()` (0 f-strings), e.g. `"Task " + str(task_id) + " is already completed"` |
| Calling between modules | methods on objects: `_manager.add_task(...)`, `storage.save(...)` | module-qualified procedures: `task_ops.add_task(store, ...)`, `storage.save_store(store)` |
| Other syntax used only here | `**task_data` unpacking (`create_task`); `global _manager` (`service.configure`); conditional expression `UrgentTask if is_high else Task` | `continue` (`filter_tasks`); `elif` (`compare_tasks`) |

## 2. Data types

* **A task.** OOP: an object of class `Task` or `UrgentTask`. It holds seven
  `_`-prefixed attributes and is turned into a `dict` only at the edge, by
  `Task.to_dict`. Imperative: a `dict` with the keys `id`, `title`,
  `description`, `due_date`, `priority`, `status` and `category`, used
  everywhere.
* **The kind of task.** OOP records "high priority" in the **type** of the
  object (`UrgentTask`), chosen by `create_task`. Imperative has one data type
  for every task, and "high priority" is just the value `task["priority"] == "high"`.
* **Due date.** Both store it as text (`"YYYY-MM-DD HH:MM"`) and turn it into
  a `datetime` object to check it and to sort. OOP does this inside the object:
  the read-only property `Task.due_datetime` calls `Task._parse_due_date`.
  Imperative calls the function `validation.parse_due_date(text)` wherever
  it is needed (`check_task_rules`, `compare_tasks`).
* **Program state.** OOP: attributes of one `TaskManager` object (`_tasks`
  list, `_next_id` int, `_storage` object). Imperative: one module-level `dict`
  `store` with the keys `"tasks"`, `"next_id"` and `"data_file"`.
* **Error types.** OOP defines four exception classes of its own. Imperative
  uses the built-in `ValueError`, `KeyError` and `OSError`.
* **File paths.** OOP uses `pathlib.Path` objects (`JsonTaskStorage`).
  Imperative uses plain `str` paths with `os.path` / `os.replace`.
* **Checking for duplicate ids when loading.** OOP uses a `set`, imperative a `list`.
* **Shared by both:** `tuple` constants (including `CATEGORIES`), the
  `PRIORITY_RANK` `dict`, and `int` ids with `bool` explicitly rejected.

## 3. Control structures

Counts *(AST)*:

| | Object-Oriented | Imperative |
|---|---|---|
| `if` statements | 38 | 55 |
| `for` loops | 3 | 11 |
| `while` loops | 0 | 3 |
| Comprehensions / generator expressions | 5 | 0 |
| Conditional expressions (`x if c else y`) | 1 | 0 |
| Recursive functions | 0 | 1 (`merge_sort`) |

The same operation, side by side:

| Operation | Object-Oriented | Imperative |
|---|---|---|
| Find a task by id | `for index, task in enumerate(self._tasks)` (`TaskManager._find_index`) | `for index in range(len(tasks))` (`task_ops.find_task_index`) |
| Search | list comprehension calling `task.matches_keyword(keyword)` (`TaskManager._search`) | `for` loop with `if` / `elif` (`query_ops.search_tasks`) |
| Filter (status, priority, category) | `filter()` with one lambda that combines three conditions with `and` (`TaskManager._filter`) | `for` loop with three `if ... continue` (`query_ops.filter_tasks`) |
| Sort | built-in `sorted()` twice: first by id, then by the key (relies on stable sorting, including with `reverse=True`) (`TaskManager._sort`) | hand-written recursive merge sort with a compare function; ties broken inside `compare_tasks` (`query_ops.merge_sort`, `merge`, `compare_tasks`) |
| Sort by due date and time | `key=lambda task: task.due_datetime` (compares `datetime` objects) | `compare_tasks` parses both due dates and compares the `datetime` objects with `<` |
| Undated tasks last | split into two lists with comprehensions, sort one, concatenate (`TaskManager._sort`) | two early `return`s in `compare_tasks` |
| High-priority rule | a subclass method: `UrgentTask.validate` | one `if` at the end of `validation.check_task_rules` |

## 4. Subprograms

* **Number and kind.** OOP has 50 methods in 8 classes plus 16 module-level
  functions: the 15 in `service.py` and `task.create_task`. Imperative has 45
  module-level functions and no methods *(AST)*.
* **How state reaches the code.** OOP methods reach state through `self`, so
  their parameter lists hold only the request data, e.g.
  `TaskManager.update_task(self, task_id, changes)`. Imperative procedures
  receive the state as an explicit parameter, e.g.
  `task_ops.update_task(store, task_id, changes)`.
* **Side effects.** Imperative procedures such as `task_ops.add_task` and
  `storage.load_store` change the `store` dict passed to them, and the caller
  sees the change because Python passes a reference. In OOP the same changes
  happen to `self._tasks` inside `TaskManager` methods.
* **The public layer.** In OOP each public function in `service.py` is one
  line that calls a `TaskManager` method and converts the result with
  `to_dict()` / `_to_dicts()`. In imperative each public function calls a
  procedure, then `storage.save_store(store)` for changes, then returns a copy.
* **Auto-save.** OOP: `TaskManager._autosave()` is called inside each changing
  method. Imperative: `storage.save_store(store)` is called from each changing
  function in `service.py`.
* **Functions as values.** OOP passes lambdas to `filter()`, `sorted()` and
  `map()`. Imperative passes a lambda to its own `merge_sort(items, compare)`
  and passes `dict` to `map()`.

## 5. Error handling

| Aspect | Object-Oriented | Imperative |
|---|---|---|
| Types raised | `TaskValidationError`, `TaskNotFoundError`, `TaskStorageError` (all subclasses of `TaskError`) | `ValueError`, `KeyError`, `OSError` |
| Link to the built-in types | each custom class also inherits from `ValueError`, `KeyError` or `OSError` (multiple inheritance in `exceptions.py`) | uses them directly |
| Message for "not found" | built by `TaskNotFoundError.__init__(task_id)` | built at the `raise` in `task_ops.find_task_index` |
| `KeyError` printing | `TaskError.__str__` is overridden so `str(error)` has no extra quotes | `str(KeyError(...))` adds quotes, so the servers read `error.args[0]` (which works for both backends) |
| Invalid date or time | `Task._parse_due_date` catches the `ValueError` from `strptime` and returns `None`; `Task.validate` then raises `TaskValidationError` | `validation.parse_due_date` catches the `ValueError` and returns `None`; `check_task_rules` then raises `ValueError` |
| `raise` statements *(AST)* | 31 | 31 |
| `try` blocks *(AST)* | 4 | 4 |
| Error chaining | `raise ... from error` in `storage.py` and `task_manager.py` | `raise ... from error` in `storage.py` |
| Keeping data safe on failure | `update_task` builds a new object first and replaces the old one only if it validates; `load` replaces `_tasks` only after every record is built | `update_task` builds and validates a merged dict first; `load_store` replaces `store["tasks"]` only after every record is cleaned |

Because the custom OOP exceptions inherit from the built-in types, both
servers use the same `status_code_for` function with three `isinstance` checks.

## 6. Readability

Observations about how the code is laid out:

* **Where the task rules are.** In OOP they are split between
  `Task._clean_text` (type checks), `Task.validate` (general rules, including
  the category), `Task._parse_due_date` (date and time), `UrgentTask.validate`
  (the high-priority rule) and `create_task` (unknown fields, choosing the
  class). In imperative they are in one module, `validation.py`, mainly in
  `clean_task_data`, `check_task_rules` and `parse_due_date`.
* **Following a call.** For the OOP high-priority rule you have to know that
  `Task.__init__` calls `self.validate()` and that Python picks
  `UrgentTask.validate` for urgent tasks. The imperative rule is a direct `if`
  in the function that is called.
* **Data flow.** Imperative function signatures show every piece of data a
  procedure uses (`store`, `tasks`, `task_id`, ...). OOP signatures leave out
  the state because it lives in `self`.
* **Naming.** Field access reads as `task.title` (OOP) vs `task["title"]`
  (imperative). OOP marks internal helpers with a leading underscore
  (`_find_index`, `_sort`). The imperative modules have no such marking; every
  function is module-level and public.
* **Sorting.** The OOP sort is one method, `TaskManager._sort` (20 lines
  including its docstring and comments), built on `sorted()`. The imperative
  sort is spread over `compare_tasks`, `merge_sort`, `merge` and `sort_tasks`
  (76 lines including docstrings and comments), and every step of the
  algorithm is written out.

## 7. Maintainability

Concrete changes and what each backend needed or would need. The first row is
the **category** field that was actually added to both backends.

| Change | Object-Oriented | Imperative |
|---|---|---|
| Add a new task field (done for `category`) | `CATEGORIES` and `EDITABLE_FIELDS` in `constants.py`; `Task.__init__` parameter and attribute; a new `@property`; two checks in `Task.validate`; `Task.to_dict`; `TaskManager._filter`, `filter_tasks`, `query_tasks`; `service.py` (`get_options`, `filter_tasks`, `query_tasks`) | `CATEGORIES` and `EDITABLE_FIELDS` in `constants.py`; the defaults dict in `validation.clean_task_data`; two checks in `validation.check_task_rules`; `query_ops.filter_tasks`, `query_tasks`; `service.py` (`get_options`, `filter_tasks`, `query_tasks`) |
| Change the due date format (done: added the time) | `DUE_DATE_FORMAT` in `constants.py`; `Task._parse_due_date`; new `Task.due_datetime` property; the sort key in `TaskManager._sort` | `DUE_DATE_FORMAT` in `constants.py`; `validation.parse_due_date`; the due-date branch of `query_ops.compare_tasks` |
| Add a new kind of task with extra rules | a new subclass overriding `validate`, plus a branch in `create_task` | another `if` in `validation.check_task_rules` |
| Change the save format | `JsonTaskStorage` in `storage.py` only | `storage.py` only |
| Stop outside code from changing stored tasks | handled by read-only properties and `to_dict()` returning new dicts | must copy explicitly (`service.copy_tasks`, `dict(task)`), because the stored dicts are mutable and would otherwise be shared |
| Add a second, independent task list | create another `TaskManager` object | the procedures already take `store` as a parameter, but `service.py` has only one module-level `store` |

Both backends keep their own copy of `constants.py`, so each system can be read
and run without the other.

## 8. Code size

From `python docs/count_lines.py`. "Code" excludes blank lines,
comment-only lines and docstrings.

### Object-Oriented (`system_oop/backend/`)

| File | Total | Code | Comments | Docstrings | Blank |
|---|---:|---:|---:|---:|---:|
| `__init__.py` | 6 | 0 | 0 | 5 | 1 |
| `constants.py` | 26 | 12 | 4 | 4 | 6 |
| `exceptions.py` | 38 | 12 | 0 | 14 | 12 |
| `service.py` | 111 | 51 | 4 | 22 | 34 |
| `storage.py` | 97 | 61 | 4 | 15 | 17 |
| `task.py` | 201 | 123 | 12 | 32 | 34 |
| `task_manager.py` | 226 | 144 | 16 | 28 | 38 |
| **Total (7 files)** | **705** | **403** | **40** | **120** | **142** |

### Imperative (`system_imperative/backend/`)

| File | Total | Code | Comments | Docstrings | Blank |
|---|---:|---:|---:|---:|---:|
| `__init__.py` | 6 | 0 | 0 | 5 | 1 |
| `constants.py` | 26 | 12 | 4 | 4 | 6 |
| `query_ops.py` | 134 | 83 | 6 | 21 | 24 |
| `service.py` | 131 | 65 | 3 | 27 | 36 |
| `storage.py` | 112 | 75 | 5 | 11 | 21 |
| `task_ops.py` | 80 | 44 | 3 | 14 | 19 |
| `validation.py` | 173 | 110 | 6 | 23 | 34 |
| **Total (7 files)** | **662** | **389** | **27** | **105** | **141** |

The OOP backend has 14 more code lines (403 vs 389). The lines are spread
differently:

* OOP spends lines on class structure: nine `@property` methods (eight in
  `task.py`), four exception classes in `exceptions.py`, and `to_dict`
  conversions in `service.py`.
* Imperative spends lines on explicit control flow: the merge sort in
  `query_ops.py` (`merge_sort` + `merge` + `compare_tasks`) and loop-based
  search and filter.

Run `python docs/count_lines.py` again after changing either backend to
update these numbers.

## 9. The comparison app (`system_compare/`)

A third React front end (port 5175) that shows both systems at once. It adds no
logic of its own, and it has **no backend**: it only calls the two systems'
servers (5001 and 5002). Its components (`TaskForm`, `Toolbar`, `TaskList`,
`TaskItem`, `MessageBanner`) and `styles.css` are unchanged copies of the
systems' files, and `tests/test_frontends_match.py` checks that they stay
identical.

* **Normal mode.** Pick OOP or Imperative; one system is shown full width, like
  its own front end. The header shows the active system and its server port.
* **Compare mode.** The screen splits into a left half (OOP, port 5001) and a
  right half (Imperative, port 5002).
  * **Shared controls.** One shared add form and one shared toolbar (search,
    filter, sort, save, load) send every action to both servers. Each half
    shows its own server's answer.
  * **Per-task actions.** Edit, complete and delete are buttons on each task
    inside a half, and only call that half's server. Editing opens the same
    task form inside that half. This is needed because the same task can have
    a different id in each system. For example, if one server was down while a
    task was added, the next task gets id 2 in one system and id 1 in the other.
  * **Separate state and errors.** Each half keeps its own state (the
    `useSystem` hook in `src/useSystem.js`), so messages and errors stay in
    their own half. If one server is not running, that half shows "Cannot
    connect to the server on port 500X" and the other half keeps working.

What the comparison app makes visible:

* For the same input, both halves show the same results, the same sort
  order and the same error messages, because both backends follow one
  contract.
* Where the systems' data differs (different ids, or a task missing from one
  side), the halves show it directly.
