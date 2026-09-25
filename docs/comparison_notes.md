# Comparison Notes: Object-Oriented vs Imperative Backend

These notes compare only the two backends (`backend_oop/` and
`backend_imperative/`), not the React front end or the API. Every statement
refers to code in this repository. Counts marked *(AST)* were taken by parsing
the source with Python's `ast` module; line counts come from
`python docs/count_lines.py`.

Both backends implement the same contract
([`contract/backend_contract.py`](../contract/backend_contract.py)) and give
identical results and error messages for the same calls. This is checked by
[`tests/test_parity.py`](../tests/test_parity.py) and by the 75 shared test
cases in [`tests/shared_cases.py`](../tests/shared_cases.py), which run against
both backends.

---

## 1. Syntax

| Aspect | Object-Oriented | Imperative |
|---|---|---|
| Main building block | `class` (8 classes *(AST)*) | `def` at module level (45 functions *(AST)*) |
| Reading a field | attribute access through a property: `task.status` | dictionary subscript: `task["status"]` |
| Reaching shared state | through `self`: `self._tasks`, `self._next_id` | through a parameter: `store["tasks"]`, `store["next_id"]` |
| Decorators | `@property` ×7, `@staticmethod` ×7, `@classmethod` ×1 | none |
| Calling the parent version | `super().validate()` in `UrgentTask.validate`; `super().__init__(message)` in `TaskError.__init__` | not applicable |
| Building messages | f-strings (14 *(AST)*), e.g. `f"Task {self._id} is already completed"` | `+` and `str()` (0 f-strings), e.g. `"Task " + str(task_id) + " is already completed"` |
| Calling between modules | methods on objects: `_manager.add_task(...)`, `storage.save(...)` | module-qualified procedures: `task_ops.add_task(store, ...)`, `storage.save_store(store)` |
| Other syntax used only here | `**task_data` unpacking (`create_task`); `global _manager` (`service.configure`); conditional expression `UrgentTask if is_high else Task` | `continue` (`filter_tasks`); `elif` (`compare_tasks`) |

## 2. Data types

* **A task.** OOP: an object of class `Task` or `UrgentTask`. It holds six
  `_`-prefixed attributes and is turned into a `dict` only at the edge, by
  `Task.to_dict`. Imperative: a `dict` with the keys `id`, `title`,
  `description`, `due_date`, `priority` and `status`, used everywhere.
* **The kind of task.** OOP records "high priority" in the **type** of the
  object (`UrgentTask`), chosen by `create_task`. Imperative has one data type
  for every task, and "high priority" is just the value `task["priority"] == "high"`.
* **Program state.** OOP: attributes of one `TaskManager` object (`_tasks`
  list, `_next_id` int, `_storage` object). Imperative: one module-level `dict`
  `store` with the keys `"tasks"`, `"next_id"` and `"data_file"`.
* **Error types.** OOP defines four exception classes of its own. Imperative
  uses the built-in `ValueError`, `KeyError` and `OSError`.
* **File paths.** OOP uses `pathlib.Path` objects (`JsonTaskStorage`).
  Imperative uses plain `str` paths with `os.path` / `os.replace`.
* **Checking for duplicate ids when loading.** OOP uses a `set`, imperative a `list`.
* **Shared by both:** `tuple` constants, the `PRIORITY_RANK` `dict`, `int` ids
  (with `bool` explicitly rejected), and dates stored as `"YYYY-MM-DD"`
  strings, which sort correctly as text.

## 3. Control structures

Counts *(AST)*:

| | Object-Oriented | Imperative |
|---|---|---|
| `if` statements | 34 | 51 |
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
| Filter | `filter()` with a lambda (`TaskManager._filter`) | `for` loop with two `if ... continue` (`query_ops.filter_tasks`) |
| Sort | built-in `sorted()` twice: first by id, then by the key (relies on stable sorting, including with `reverse=True`) (`TaskManager._sort`) | hand-written recursive merge sort with a compare function; ties broken inside `compare_tasks` (`query_ops.merge_sort`, `merge`, `compare_tasks`) |
| Undated tasks last | split into two lists with comprehensions, sort one, concatenate (`TaskManager._sort`) | two early `return`s in `compare_tasks` |
| High-priority rule | a subclass method: `UrgentTask.validate` | one `if` at the end of `validation.check_task_rules` |

## 4. Subprograms

* **Number and kind.** OOP has 48 methods in 8 classes plus 16 module-level
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
| `KeyError` printing | `TaskError.__str__` is overridden so `str(error)` has no extra quotes | `str(KeyError(...))` adds quotes, so the API reads `error.args[0]` (which works for both backends) |
| `raise` statements *(AST)* | 29 | 29 |
| `try` blocks *(AST)* | 4 | 4 |
| Error chaining | `raise ... from error` in `storage.py` and `task_manager.py` | `raise ... from error` in `storage.py` |
| Keeping data safe on failure | `update_task` builds a new object first and replaces the old one only if it validates; `load` replaces `_tasks` only after every record is built | `update_task` builds and validates a merged dict first; `load_store` replaces `store["tasks"]` only after every record is cleaned |

Because the custom OOP exceptions inherit from the built-in types, the API
handles both backends with the same three checks (`api/backend_registry.py`
→ `status_code_for`).

## 6. Readability

Observations about how the code is laid out:

* **Where the task rules are.** In OOP they are split between
  `Task._clean_text` (type checks), `Task.validate` (general rules),
  `UrgentTask.validate` (the high-priority rule) and `create_task` (unknown
  fields, choosing the class). In imperative they are in one module,
  `validation.py`, in two functions: `clean_task_data` and `check_task_rules`.
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
* **Sorting.** The OOP sort is one method, `TaskManager._sort` (18 lines
  including its docstring and comments), built on `sorted()`. The imperative
  sort is spread over `compare_tasks`, `merge_sort`, `merge` and `sort_tasks`
  (75 lines including docstrings and comments), and every step of the
  algorithm is written out.

## 7. Maintainability

Concrete changes and what each backend would need:

| Change | Object-Oriented | Imperative |
|---|---|---|
| Add a new task field | `EDITABLE_FIELDS` in `constants.py`; `Task.__init__` parameter and attribute; a new `@property`; `Task.validate`; `Task.to_dict` | `EDITABLE_FIELDS` in `constants.py`; the defaults dict in `validation.clean_task_data`; `validation.check_task_rules` |
| Add a new kind of task with extra rules | a new subclass overriding `validate`, plus a branch in `create_task` | another `if` in `validation.check_task_rules` |
| Change the save format | `JsonTaskStorage` in `storage.py` only | `storage.py` only |
| Stop outside code from changing stored tasks | handled by read-only properties and `to_dict()` returning new dicts | must copy explicitly (`service.copy_tasks`, `dict(task)`), because the stored dicts are mutable and would otherwise be shared |
| Add a second, independent task list | create another `TaskManager` object | the procedures already take `store` as a parameter, but `service.py` has only one module-level `store` |

Both backends keep their own copy of `constants.py`, so each can be read and
run without the other.

## 8. Code size

From `python docs/count_lines.py`. "Code" excludes blank lines,
comment-only lines and docstrings.

### Object-Oriented (`backend_oop/`)

| File | Total | Code | Comments | Docstrings | Blank |
|---|---:|---:|---:|---:|---:|
| `__init__.py` | 5 | 0 | 0 | 4 | 1 |
| `constants.py` | 22 | 10 | 2 | 4 | 6 |
| `exceptions.py` | 38 | 12 | 0 | 14 | 12 |
| `service.py` | 109 | 49 | 4 | 22 | 34 |
| `storage.py` | 97 | 61 | 4 | 15 | 17 |
| `task.py` | 176 | 105 | 9 | 30 | 32 |
| `task_manager.py` | 222 | 141 | 15 | 28 | 38 |
| **Total (7 files)** | **669** | **378** | **34** | **117** | **140** |

### Imperative (`backend_imperative/`)

| File | Total | Code | Comments | Docstrings | Blank |
|---|---:|---:|---:|---:|---:|
| `__init__.py` | 5 | 0 | 0 | 4 | 1 |
| `constants.py` | 22 | 10 | 2 | 4 | 6 |
| `query_ops.py` | 130 | 80 | 5 | 21 | 24 |
| `service.py` | 129 | 63 | 3 | 27 | 36 |
| `storage.py` | 112 | 75 | 5 | 11 | 21 |
| `task_ops.py` | 80 | 44 | 3 | 14 | 19 |
| `validation.py` | 160 | 101 | 3 | 22 | 34 |
| **Total (7 files)** | **638** | **373** | **21** | **103** | **141** |

The two backends have almost the same number of code lines (378 vs 373),
but spread differently:

* OOP spends lines on class structure: six `@property` methods for the task
  fields in `task.py`, four exception classes in `exceptions.py`, and `to_dict`
  conversions in `service.py`.
* Imperative spends lines on explicit control flow: the merge sort in
  `query_ops.py` (`merge_sort` + `merge` + `compare_tasks`) and loop-based
  search and filter.

Run `python docs/count_lines.py` again after changing either backend to
update these numbers.
