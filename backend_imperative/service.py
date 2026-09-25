"""
Public interface of the imperative backend.

Every function here is listed in contract/backend_contract.py and has the same
name, parameters and return format as in backend_oop/service.py.

All of this backend's data lives in the `store` dictionary below. Each public
function passes the store to a procedure that changes it step by step, then
saves it, then returns a copy of the result.
"""

import os

from . import query_ops, storage, task_ops, validation
from .constants import (
    DEFAULT_PRIORITY,
    DEFAULT_STATUS,
    PRIORITIES,
    SORT_FIELDS,
    STATUSES,
)

# The whole state of this backend: a list of task dictionaries, the next free
# id, and the path of the save file.
store = {
    "tasks": [],
    "next_id": 1,
    "data_file": None,
}


def copy_tasks(tasks):
    """
    Return copies of the task dictionaries.

    Python passes references, so without copies a caller could change our
    stored tasks by editing the dictionaries we return.
    """
    # map() is a higher-order function: it applies dict() to every task.
    return list(map(dict, tasks))


def configure(data_file):
    """Use `data_file` as the save file, start fresh, and load any saved tasks."""
    validation.check_data_file(data_file)
    store["tasks"] = []
    store["next_id"] = 1
    store["data_file"] = os.fspath(data_file)
    return {"loaded": storage.load_store(store)}


def get_options():
    """Return the allowed priorities, statuses and sort fields, and the defaults."""
    return {
        "priorities": list(PRIORITIES),
        "statuses": list(STATUSES),
        "sort_fields": list(SORT_FIELDS),
        "defaults": {"priority": DEFAULT_PRIORITY, "status": DEFAULT_STATUS},
    }


def add_task(task_data):
    """Create a task from a dictionary of fields and return it."""
    task = task_ops.add_task(store, task_data)
    storage.save_store(store)
    return dict(task)


def get_all_tasks():
    """Return every task."""
    return copy_tasks(store["tasks"])


def get_task(task_id):
    """Return the task with the given id."""
    return dict(task_ops.get_task(store["tasks"], task_id))


def update_task(task_id, changes):
    """Change some fields of a task and return the updated task."""
    task = task_ops.update_task(store, task_id, changes)
    storage.save_store(store)
    return dict(task)


def complete_task(task_id):
    """Mark a task as completed and return it."""
    task = task_ops.complete_task(store, task_id)
    storage.save_store(store)
    return dict(task)


def delete_task(task_id):
    """Delete a task and return the task that was deleted."""
    task = task_ops.delete_task(store, task_id)
    storage.save_store(store)
    return dict(task)


def search_tasks(keyword):
    """Return tasks whose title or description contains the keyword."""
    return copy_tasks(query_ops.search_tasks(store["tasks"], keyword))


def filter_tasks(status=None, priority=None):
    """Return tasks with the given status and/or priority."""
    return copy_tasks(query_ops.filter_tasks(store["tasks"], status, priority))


def sort_tasks(sort_by, descending=False):
    """Return all tasks sorted by "due_date" or "priority"."""
    return copy_tasks(query_ops.sort_tasks(store["tasks"], sort_by, descending))


def query_tasks(keyword=None, status=None, priority=None, sort_by=None,
                descending=False):
    """Search, filter and sort in one call."""
    return copy_tasks(query_ops.query_tasks(
        store["tasks"], keyword, status, priority, sort_by, descending))


def save_tasks():
    """Save all tasks to the data file."""
    return {"saved": storage.save_store(store)}


def load_tasks():
    """Reload all tasks from the data file."""
    return {"loaded": storage.load_store(store)}
