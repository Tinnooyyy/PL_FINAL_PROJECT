"""
The shared backend contract.

This file is the ONE place where the public interface of both backends is
defined. `system_oop/backend/service.py` and
`system_imperative/backend/service.py` must each expose every function listed
in CONTRACT, with exactly the parameter list shown.
`tests/test_contract.py` checks this automatically.

Neither system imports this file; it is a specification that only the tests
and the documentation refer to.


TASK FORMAT
-----------
Every function that returns a task returns a plain dictionary with exactly
these keys, in this order:

    {
        "id":          int,   # assigned by the backend, starts at 1
        "title":       str,   # required, 1-100 characters after trimming
        "description": str,   # optional, up to 500 characters ("" if empty)
        "due_date":    str,   # "YYYY-MM-DD HH:MM" (24-hour), or "" for none
        "priority":    str,   # "low" | "medium" | "high"   (default "medium")
        "status":      str,   # "pending" | "in_progress" | "completed"
                              #                              (default "pending")
        "category":    str,   # "personal" | "academic" | "work"  (required)
    }

Lists of tasks are returned as Python lists of these dictionaries.


BUSINESS RULES (enforced identically by both backends)
------------------------------------------------------
* The title is required and may not be blank or longer than 100 characters.
* The description may not be longer than 500 characters.
* A due date, when given, must be a real date AND time written exactly as
  "YYYY-MM-DD HH:MM" (24-hour clock), e.g. "2026-10-05 14:30". A date
  without a time is rejected. It is checked by parsing it with datetime.
* Priority, status and category must be one of the allowed values
  (case-insensitive on input, always stored in lowercase).
* The category is required: there is no default.
* A HIGH-priority task must have a due date.
* Task data may only contain the fields title, description, due_date,
  priority, status and category. Any other key is rejected.
* Checks run in this order, and the first failure is reported: title,
  description, due date, priority, status, category, then the high-priority
  rule.
* Completing a task that is already completed is an error.
* Search is case-insensitive and looks in the title and the description.
* Sorting: ties are broken by id (ascending). Sorting by due date compares
  the full date and time. Tasks with no due date are always placed last when
  sorting by due date, in either direction.
* Priority order is low < medium < high.
* Every change (add, update, complete, delete) is saved to the data file
  automatically.


ERRORS
------
Both backends signal errors by raising exceptions that are (or inherit from)
these three built-in types. Each system's server maps them to HTTP status codes.

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

    # The allowed values and defaults, so the front end does not have to
    # hard-code them. Returns
    # {"priorities": [...], "statuses": [...], "categories": [...],
    #  "sort_fields": [...],
    #  "defaults": {"priority": "medium", "status": "pending"}}
    # (category has no default because it is required)
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

    # Returns tasks matching every given filter (status, priority, category).
    # None (or "") means "do not filter on this field".
    "filter_tasks": "(status=None, priority=None, category=None)",

    # Returns all tasks sorted by "due_date" or "priority".
    # descending may be a bool or the text "true"/"false".
    "sort_tasks": "(sort_by, descending=False)",

    # Search, then filter, then sort, in a single call. Any argument that is
    # None (or "") skips that step. This is what the React UI uses.
    "query_tasks": (
        "(keyword=None, status=None, priority=None, category=None, "
        "sort_by=None, descending=False)"
    ),

    # Write all tasks to the data file. Returns {"saved": <number of tasks>}
    "save_tasks": "()",

    # Replace the tasks in memory with the ones in the data file.
    # Returns {"loaded": <number of tasks>}
    "load_tasks": "()",
}

# The keys of a task dictionary, in the order both backends return them.
TASK_FIELDS = ["id", "title", "description", "due_date", "priority", "status",
               "category"]
