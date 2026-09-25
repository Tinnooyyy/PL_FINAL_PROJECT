"""
Public interface of the object-oriented backend.

Every function here is listed in contract/backend_contract.py and has the same
name, parameters and return format as in system_imperative/backend/service.py.

These functions are a thin layer over one TaskManager object: they call a
method and convert the Task objects that come back into plain dictionaries.
"""

from .constants import (
    CATEGORIES,
    DEFAULT_PRIORITY,
    DEFAULT_STATUS,
    PRIORITIES,
    SORT_FIELDS,
    STATUSES,
)
from .storage import JsonTaskStorage
from .task_manager import TaskManager

# The single manager object that holds this backend's tasks.
_manager = TaskManager()


def _to_dicts(tasks):
    """Convert a list of Task objects into a list of dictionaries."""
    # map() is a higher-order function: it applies the lambda to every task.
    return list(map(lambda task: task.to_dict(), tasks))


def configure(data_file):
    """Use `data_file` as the save file, start fresh, and load any saved tasks."""
    global _manager
    # JsonTaskStorage checks the path first, so a bad path leaves the
    # current manager in place.
    _manager = TaskManager(JsonTaskStorage(data_file))
    return {"loaded": _manager.load()}


def get_options():
    """Return the allowed priorities, statuses, categories and sort fields, and the defaults."""
    return {
        "priorities": list(PRIORITIES),
        "statuses": list(STATUSES),
        "categories": list(CATEGORIES),
        "sort_fields": list(SORT_FIELDS),
        "defaults": {"priority": DEFAULT_PRIORITY, "status": DEFAULT_STATUS},
    }


def add_task(task_data):
    """Create a task from a dictionary of fields and return it."""
    return _manager.add_task(task_data).to_dict()


def get_all_tasks():
    """Return every task."""
    return _to_dicts(_manager.get_all_tasks())


def get_task(task_id):
    """Return the task with the given id."""
    return _manager.get_task(task_id).to_dict()


def update_task(task_id, changes):
    """Change some fields of a task and return the updated task."""
    return _manager.update_task(task_id, changes).to_dict()


def complete_task(task_id):
    """Mark a task as completed and return it."""
    return _manager.complete_task(task_id).to_dict()


def delete_task(task_id):
    """Delete a task and return the task that was deleted."""
    return _manager.delete_task(task_id).to_dict()


def search_tasks(keyword):
    """Return tasks whose title or description contains the keyword."""
    return _to_dicts(_manager.search_tasks(keyword))


def filter_tasks(status=None, priority=None, category=None):
    """Return tasks with the given status, priority and/or category."""
    return _to_dicts(_manager.filter_tasks(status, priority, category))


def sort_tasks(sort_by, descending=False):
    """Return all tasks sorted by "due_date" or "priority"."""
    return _to_dicts(_manager.sort_tasks(sort_by, descending))


def query_tasks(keyword=None, status=None, priority=None, category=None,
                sort_by=None, descending=False):
    """Search, filter and sort in one call."""
    return _to_dicts(_manager.query_tasks(keyword, status, priority, category,
                                          sort_by, descending))


def save_tasks():
    """Save all tasks to the data file."""
    return {"saved": _manager.save()}


def load_tasks():
    """Reload all tasks from the data file."""
    return {"loaded": _manager.load()}
