"""
The shared backend contract.

This file is the ONE place where the public interface of both backends is
defined. `backend_oop/service.py` and `backend_imperative/service.py` must
each expose every function listed in CONTRACT, with exactly the parameter
list shown. `tests/test_contract.py` checks this automatically.

Nothing here is executed by the backends; it is a specification that the
tests and the documentation refer to.


TASK FORMAT
-----------
Every function that returns a task returns a plain dictionary with exactly
these keys, in this order:

    {
        "id":          int,   # assigned by the backend, starts at 1
        "title":       str,   # required, 1-100 characters after trimming
        "description": str,   # optional, up to 500 characters ("" if empty)
        "due_date":    str,   # "YYYY-MM-DD", or "" for no due date
        "priority":    str,   # "low" | "medium" | "high"   (default "medium")
        "status":      str,   # "pending" | "in_progress" | "completed"
                              #                              (default "pending")
    }

Lists of tasks are returned as Python lists of these dictionaries.


BUSINESS RULES (enforced identically by both backends)
------------------------------------------------------
* The title is required and may not be blank or longer than 100 characters.
* The description may not be longer than 500 characters.
* A due date, when given, must be a real calendar date in YYYY-MM-DD form.
* Priority and status must be one of the allowed values (case-insensitive
  on input, always stored in lowercase).
* A HIGH-priority task must have a due date.
* Task data may only contain the fields title, description, due_date,
  priority and status. Any other key is rejected.
* Completing a task that is already completed is an error.
* Search is case-insensitive and looks in the title and the description.
* Sorting: ties are broken by id (ascending). Tasks with no due date are
  always placed last when sorting by due date, in either direction.
* Priority order is low < medium < high.
* Every change (add, update, complete, delete) is saved to the data file
  automatically.


ERRORS
------
Both backends signal errors by raising exceptions that are (or inherit from)
these three built-in types. The API maps them to HTTP status codes.

    ValueError  -> invalid input                         (HTTP 400)
    KeyError    -> task id not found                     (HTTP 404)
    OSError     -> save file cannot be read or written   (HTTP 500)

The first argument of the exception (error.args[0]) is a human-readable
message that can be shown to the user.

The OOP backend raises its own exception classes, which inherit from these
built-in types. The imperative backend raises the built-in types directly.
"""

# Function name -> exact parameter list (as printed by inspect.signature).
CONTRACT = {
    # Point the backend at a save file and load it.
    # Returns {"loaded": <number of tasks loaded>}
    "configure": "(data_file)",

    # The allowed values, so the front end does not have to hard-code them.
    # Returns {"priorities": [...], "statuses": [...], "sort_fields": [...]}
    "get_options": "()",

    # Create a task. task_data is a dict with any of the task fields except id.
    # Returns the new task.
    "add_task": "(task_data)",

    # Returns a list of all tasks, in the order they were added.
    "get_all_tasks": "()",

    # Returns one task.
    "get_task": "(task_id)",

    # Change one or more fields of a task. Returns the updated task.
    "update_task": "(task_id, changes)",

    # Set the status to "completed". Returns the updated task.
    "complete_task": "(task_id)",

    # Remove a task. Returns the task that was removed.
    "delete_task": "(task_id)",

    # Returns tasks whose title or description contains the keyword.
    # A blank keyword returns all tasks.
    "search_tasks": "(keyword)",

    # Returns tasks matching the given status and/or priority.
    # None (or "") means "do not filter on this field".
    "filter_tasks": "(status=None, priority=None)",

    # Returns all tasks sorted by "due_date" or "priority".
    # descending may be a bool or the text "true"/"false".
    "sort_tasks": "(sort_by, descending=False)",

    # Search, then filter, then sort, in a single call. Any argument that is
    # None (or "") skips that step. This is what the React UI uses.
    "query_tasks": (
        "(keyword=None, status=None, priority=None, sort_by=None, "
        "descending=False)"
    ),

    # Write all tasks to the data file. Returns {"saved": <number of tasks>}
    "save_tasks": "()",

    # Replace the tasks in memory with the ones in the data file.
    # Returns {"loaded": <number of tasks>}
    "load_tasks": "()",
}

# The keys of a task dictionary, in the order both backends return them.
TASK_FIELDS = ["id", "title", "description", "due_date", "priority", "status"]
