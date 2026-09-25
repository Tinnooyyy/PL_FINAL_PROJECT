"""
Procedures that change the task list (imperative backend).

Every procedure receives the `store` dictionary (or its list of tasks) as a
parameter and changes it directly. Python passes a reference to the same
dictionary, so the caller sees the changes without anything being returned.

The store looks like:
    {"tasks": [ {task}, {task}, ... ], "next_id": 4, "data_file": "..."}
"""

from . import validation
from .constants import EDITABLE_FIELDS


def find_task_index(tasks, task_id):
    """Return the list position of the task with this id, or raise KeyError."""
    validation.check_task_id(task_id)
    for index in range(len(tasks)):
        if tasks[index]["id"] == task_id:
            return index
    raise KeyError("Task with id " + str(task_id) + " was not found")


def get_task(tasks, task_id):
    """Return the task dictionary with this id."""
    index = find_task_index(tasks, task_id)
    return tasks[index]


def add_task(store, task_data):
    """Validate task_data, append it to store["tasks"] with a new id, and return it."""
    cleaned = validation.clean_task_data(task_data)

    new_task = {"id": store["next_id"]}  # put "id" first so the key order matches
    new_task.update(cleaned)

    store["tasks"].append(new_task)
    store["next_id"] = store["next_id"] + 1
    return new_task


def update_task(store, task_id, changes):
    """Apply a dictionary of changes to one task and return the updated task."""
    tasks = store["tasks"]
    index = find_task_index(tasks, task_id)
    if not isinstance(changes, dict):
        raise ValueError("Changes must be an object")
    if len(changes) == 0:
        raise ValueError("No changes were provided")

    # Step 1: copy the current values.
    merged = {}
    for field in EDITABLE_FIELDS:
        merged[field] = tasks[index][field]
    # Step 2: overwrite them with the changes.
    for key in changes:
        merged[key] = changes[key]
    # Step 3: validate the result. If this raises, the stored task is untouched.
    cleaned = validation.clean_task_data(merged)

    updated = {"id": task_id}
    updated.update(cleaned)
    tasks[index] = updated
    return updated


def complete_task(store, task_id):
    """Set a task's status to "completed" and return it."""
    task = get_task(store["tasks"], task_id)
    if task["status"] == "completed":
        raise ValueError("Task " + str(task_id) + " is already completed")
    task["status"] = "completed"
    return task


def delete_task(store, task_id):
    """Remove a task from the list and return it."""
    index = find_task_index(store["tasks"], task_id)
    return store["tasks"].pop(index)
