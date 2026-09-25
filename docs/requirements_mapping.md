# Requirements Mapping

Where each required construct and paradigm feature appears in each backend.
Paths are relative to the project root. `Class.method` means a method inside
a class; a plain name means a module-level function.

Counts marked *(AST)* were taken by parsing the source with Python's `ast`
module; line counts come from [`docs/count_lines.py`](count_lines.py).

---

## 1. The ten minimum constructs

### 1.1 Variables and appropriate data types

| | Object-Oriented (`backend_oop/`) | Imperative (`backend_imperative/`) |
|---|---|---|
| Constants | `constants.py`: `PRIORITIES`, `STATUSES`, `SORT_FIELDS`, `EDITABLE_FIELDS` (tuple), `PRIORITY_RANK` (dict), `MAX_TITLE_LENGTH` (int), `DATE_FORMAT` (str) | `constants.py`: the same names and types |
| Task fields | `task.py` → `Task.__init__`: `self._id` (int), `self._title`, `self._description`, `self._due_date`, `self._priority`, `self._status` (str) | `task_ops.py` → `add_task`: `new_task` dict with the keys `"id"` (int) and the five text fields (str) |
| Program state | `task_manager.py` → `TaskManager.__init__`: `self._tasks` (list), `self._next_id` (int), `self._storage` (object or `None`) | `service.py`: module variable `store` (dict with `"tasks"` list, `"next_id"` int, `"data_file"` str or `None`) |
| Booleans | `task_manager.py` → `TaskManager._parse_bool`; `task.py` → `create_task` (`is_high`) | `validation.py` → `parse_bool`; `query_ops.py` → `compare_tasks` (`descending`) |
| Sets | `storage.py` → `JsonTaskStorage._check_structure` (`seen_ids = set()`) | (uses a list instead) `storage.py` → `read_save_file` (`seen_ids = []`) |

### 1.2 Input and output

| | Object-Oriented | Imperative |
|---|---|---|
| Input from the API | `service.py` → `add_task(task_data)`, `update_task(task_id, changes)`, `query_tasks(...)` receive values from the API | `service.py` → the same functions |
| Output to the API | `task.py` → `Task.to_dict` builds the returned dict; `service.py` → `_to_dicts` | `service.py` → `copy_tasks` and `dict(task)` return copies |
| File write | `storage.py` → `JsonTaskStorage.save` (`Path.open("w")`, `json.dump`, `Path.replace`) | `storage.py` → `save_store` (`open(..., "w")`, `json.dump`, `os.replace`) |
| File read | `storage.py` → `JsonTaskStorage.load` (`Path.open("r")`, `json.load`) | `storage.py` → `read_save_file` (`open(..., "r")`, `json.load`) |

### 1.3 Expressions and operators

| Kind | Object-Oriented | Imperative |
|---|---|---|
| Arithmetic / assignment | `task_manager.py` → `TaskManager.add_task`: `self._next_id += 1` | `task_ops.py` → `add_task`: `store["next_id"] = store["next_id"] + 1`; `query_ops.py` → `merge_sort`: `len(items) // 2` |
| Subtraction / unary minus | — | `query_ops.py` → `compare_tasks`: `PRIORITY_RANK[...] - PRIORITY_RANK[...]`, `difference = -difference`, `first["id"] - second["id"]` |
| Comparison | `task.py` → `Task.validate`: `len(self._title) > MAX_TITLE_LENGTH` | `validation.py` → `check_task_rules`: `len(task["title"]) > MAX_TITLE_LENGTH`; `query_ops.py` → `compare_tasks`: `first_date < second_date` |
| Logical (`and` / `or` / `not`) | `task_manager.py` → `TaskManager._filter`: `(status is None or task.status == status) and (...)` | `validation.py` → `is_blank`: `value is None or (isinstance(...) and ...)` |
| Membership (`in`) | `task.py` → `Task.matches_keyword`: `keyword in self._title.lower()` | `query_ops.py` → `search_tasks`: `keyword in task["title"].lower()` |
| Conditional expression | `task.py` → `create_task`: `UrgentTask if is_high else Task` | — |
| String building | f-strings, e.g. `exceptions.py` → `TaskNotFoundError.__init__` (14 f-strings *(AST)*) | `+` concatenation with `str()`, e.g. `task_ops.py` → `find_task_index` (0 f-strings *(AST)*) |
| List concatenation | `task_manager.py` → `TaskManager._sort`: `sorted(dated, ...) + undated` | — |

### 1.4 Conditional statements

| | Object-Oriented | Imperative |
|---|---|---|
| Validation chain | `task.py` → `Task.validate` (six `if` checks) and `UrgentTask.validate` | `validation.py` → `check_task_rules` (seven `if` checks) |
| `if / elif / else` | — | `query_ops.py` → `compare_tasks` |
| `continue` inside a loop | — | `query_ops.py` → `filter_tasks` |
| Choosing a branch | `task_manager.py` → `TaskManager._sort` (`if sort_by == "priority"`), `TaskManager.query_tasks` | `query_ops.py` → `query_tasks`; `validation.py` → `parse_bool` |
| Total `if` statements *(AST)* | 34 | 51 |

### 1.5 Iteration

| | Object-Oriented | Imperative |
|---|---|---|
| `for` loop | `task_manager.py` → `TaskManager._find_index` (`enumerate`), `TaskManager.load`; `storage.py` → `JsonTaskStorage._check_structure` | `task_ops.py` → `find_task_index` (`range(len(tasks))`), `update_task`; `query_ops.py` → `search_tasks`, `filter_tasks`; `validation.py` → `clean_task_data`; `storage.py` → `read_save_file`, `load_store` |
| `while` loop | — | `query_ops.py` → `merge` (three `while` loops) |
| Comprehensions / generator expressions | `task_manager.py` → `TaskManager._search`, `TaskManager._sort`, `TaskManager.save`; `task.py` → `create_task` | — |
| Totals *(AST)* | 3 `for`, 0 `while`, 5 comprehensions | 11 `for`, 3 `while`, 0 comprehensions |

### 1.6 Functions / procedures / methods

| | Object-Oriented | Imperative |
|---|---|---|
| Kind | Methods inside classes, e.g. `Task.mark_complete`, `TaskManager.add_task`, `JsonTaskStorage.save` | Module-level procedures, e.g. `task_ops.add_task`, `query_ops.merge_sort`, `storage.save_store` |
| Counts *(AST)* | 48 methods in 8 classes, plus 16 module-level functions (15 in `service.py`, plus `task.create_task`) | 45 module-level functions, 0 methods |
| Special method kinds | `@property` ×7, `@staticmethod` ×7, `@classmethod` ×1 (`TaskManager._optional_choice`), `__init__`, `__str__`, `__repr__` | — |

### 1.7 Parameter passing

| | Object-Oriented | Imperative |
|---|---|---|
| Default parameters | `task.py` → `Task.__init__(self, task_id, title="", ..., priority=DEFAULT_PRIORITY, ...)`; `task_manager.py` → `TaskManager.filter_tasks(self, status=None, priority=None)` | `query_ops.py` → `filter_tasks(tasks, status=None, priority=None)`, `query_tasks(...)` |
| Keyword-argument unpacking | `task.py` → `create_task`: `task_class(task_id, **task_data)` | — |
| Implicit object parameter | `self` in every method | — |
| Passing an object in | `service.py` → `configure`: `TaskManager(JsonTaskStorage(data_file))` | — |
| Passing mutable state in | — | `task_ops.py` → `add_task(store, task_data)`, `update_task(store, ...)`, `complete_task(store, ...)`; `storage.py` → `load_store(store)` change the caller's dict in place |
| Passing a function in | `task_manager.py` → `TaskManager._filter` (lambda to `filter()`), `TaskManager._sort` (lambda as `key=`) | `query_ops.py` → `merge_sort(items, compare)`, `merge(left, right, compare)` |
| Protecting against aliasing | `task_manager.py` → `TaskManager.get_all_tasks` returns `list(self._tasks)`; `Task.to_dict` returns a new dict | `service.py` → `copy_tasks` (`list(map(dict, tasks))`) |

### 1.8 Appropriate data structures

| | Object-Oriented | Imperative |
|---|---|---|
| Collection of tasks | `list` of `Task` / `UrgentTask` objects (`TaskManager._tasks`) | `list` of `dict`s (`store["tasks"]`) |
| One task | a `Task` object | a `dict` |
| Lookup table | `dict` `PRIORITY_RANK` (`constants.py`) | same |
| Fixed choices | `tuple`s in `constants.py` | same |
| Unique ids while loading | `set` in `JsonTaskStorage._check_structure` | `list` in `storage.read_save_file` |
| File path | `pathlib.Path` object (`JsonTaskStorage.__init__`) | `str` with `os.path` functions (`storage.save_store`) |

### 1.9 Error / exception handling

| | Object-Oriented | Imperative |
|---|---|---|
| Error types | Custom classes in `exceptions.py`: `TaskError`, `TaskValidationError`, `TaskNotFoundError`, `TaskStorageError` | Built-in `ValueError`, `KeyError`, `OSError` |
| Raising | `task.py` → `Task.validate`, `UrgentTask.validate`, `Task.mark_complete`, `create_task`; `task_manager.py` → `TaskManager._find_index`, `update_task` | `validation.py` → `check_task_rules`, `clean_task_data`, `check_task_id`; `task_ops.py` → `find_task_index`, `update_task`, `complete_task` |
| `try / except` | `task.py` → `Task._is_valid_date`; `storage.py` → `JsonTaskStorage.save`, `JsonTaskStorage.load`; `task_manager.py` → `TaskManager.load` | `validation.py` → `is_valid_date`; `storage.py` → `save_store`, `read_save_file`, `load_store` |
| Converting one error into another (`raise ... from error`) | `storage.py` → `JsonTaskStorage.save` (`OSError` → `TaskStorageError`), `JsonTaskStorage.load` (`ValueError` / `OSError` → `TaskStorageError`); `task_manager.py` → `TaskManager.load` (`TaskValidationError` → `TaskStorageError`) | `storage.py` → `save_store` (`OSError` → `OSError` with a clearer message), `read_save_file` (`ValueError` → `OSError`), `load_store` (`ValueError` → `OSError`) |
| Counts *(AST)* | 29 `raise`, 4 `try` | 29 `raise`, 4 `try` |

### 1.10 Modular organization

| Object-Oriented | Imperative |
|---|---|
| `constants.py`: fixed values | `constants.py`: fixed values |
| `exceptions.py`: custom exception classes | `validation.py`: validation procedures |
| `task.py`: `Task`, `UrgentTask`, `create_task` | `task_ops.py`: add / update / complete / delete procedures |
| `task_manager.py`: `TaskManager` | `query_ops.py`: search / filter / sort procedures |
| `storage.py`: `JsonTaskStorage` | `storage.py`: save / load procedures |
| `service.py`: public contract functions | `service.py`: public contract functions and the `store` |

Both backends expose the same public functions, defined once in
[`contract/backend_contract.py`](../contract/backend_contract.py) and checked by
[`tests/test_contract.py`](../tests/test_contract.py).

---

## 2. Object-Oriented paradigm features (`backend_oop/`)

| Feature | Where |
|---|---|
| Classes and objects | `task.py` → `Task`, `UrgentTask`; `task_manager.py` → `TaskManager`; `storage.py` → `JsonTaskStorage`. `service.py` holds one `TaskManager` object in `_manager`. |
| A manager class that owns the task list | `task_manager.py` → `TaskManager` (`self._tasks`) |
| Encapsulation | `task.py` → `Task` stores data in `_`-prefixed attributes, exposes them through read-only `@property` methods (`id`, `title`, `description`, `due_date`, `priority`, `status`) and changes status only through `Task.mark_complete`. `TaskManager._tasks` is only reached through methods. `storage.py` → `JsonTaskStorage._path` with a `path` property. Tested in `tests/test_oop.py` → `test_properties_are_read_only`. |
| Inheritance | `task.py` → `class UrgentTask(Task)`. `exceptions.py` → `TaskValidationError(TaskError, ValueError)`, `TaskNotFoundError(TaskError, KeyError)`, `TaskStorageError(TaskError, OSError)`, all under `TaskError(Exception)`. |
| Polymorphism (method overriding) | `task.py` → `UrgentTask.validate` overrides `Task.validate` and calls `super().validate()`. `Task.__init__` calls `self.validate()`, so the subclass version runs for urgent tasks. `Task.__repr__` prints `type(self).__name__`. `exceptions.py` → `TaskError.__str__` overrides `Exception.__str__`. |
| Choosing the class at runtime | `task.py` → `create_task` returns `UrgentTask` for priority `"high"`, otherwise `Task`. `task_manager.py` → `TaskManager.update_task` rebuilds the object, so a task can change class. |
| Custom exception classes | `exceptions.py` (4 classes). `TaskNotFoundError.__init__` builds its own message from the id. |

## 3. Imperative / procedural paradigm features (`backend_imperative/`)

| Feature | Where |
|---|---|
| No user-defined classes | 0 `class` statements in the backend *(AST)*. |
| Data model is dictionaries and lists | `service.py` → `store`; `task_ops.py` → `add_task` builds each task as a `dict`. |
| State changed step by step by procedures that receive the data | `task_ops.py` → `add_task(store, task_data)` appends to `store["tasks"]` and increments `store["next_id"]`; `update_task` works in three commented steps (copy, overwrite, validate); `complete_task` sets `task["status"]`; `storage.py` → `load_store(store)` replaces `store["tasks"]`. |
| Explicit loops and conditionals where the OOP version uses methods | Finding a task: `task_ops.find_task_index` (`for index in range(len(tasks))`) vs `TaskManager._find_index`. Searching: `query_ops.search_tasks` (`for` + `if`) vs `Task.matches_keyword` + list comprehension. Filtering: `query_ops.filter_tasks` (`for` + `continue`) vs `filter()` + lambda. Sorting: `query_ops.merge_sort` / `merge` (recursion + `while`) vs `sorted()`. |
| Built-in exceptions and `try / except` | `ValueError` in `validation.py` and `task_ops.py`; `KeyError` in `task_ops.find_task_index`; `OSError` in `storage.py`. `try / except` in `validation.is_valid_date`, `storage.save_store`, `storage.read_save_file`, `storage.load_store`. |

## 4. Optional constructs (used only where they fit)

| Construct | Object-Oriented | Imperative |
|---|---|---|
| Recursion | Not used | `query_ops.py` → `merge_sort` calls itself on each half of the list |
| Lambda expressions *(AST)* | 5: `service.py` → `_to_dicts`; `task_manager.py` → `TaskManager._filter` (1) and `TaskManager._sort` (3) | 1: `query_ops.py` → `sort_tasks` |
| Higher-order functions | `map()` in `service._to_dicts`; `filter()` in `TaskManager._filter`; `sorted(key=...)` in `TaskManager._sort` | `merge_sort(items, compare)` and `merge(..., compare)` take a function; `map(dict, tasks)` in `service.copy_tasks` |
