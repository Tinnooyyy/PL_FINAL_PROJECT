"""
Saving and loading the store as JSON (imperative backend).

File problems are reported with the built-in OSError.
"""

import json
import os

from . import validation


def require_data_file(store):
    """Return the configured file path, or raise OSError if there is none."""
    if store["data_file"] is None:
        raise OSError("No data file has been configured")
    return store["data_file"]


def save_store(store):
    """Write the tasks and the next free id to the data file; return the task count."""
    path = require_data_file(store)
    file_name = os.path.basename(path)
    data = {"next_id": store["next_id"], "tasks": store["tasks"]}

    try:
        folder = os.path.dirname(path)
        if folder != "":
            os.makedirs(folder, exist_ok=True)
        # Write to a temporary file first and then swap it in, so a crash
        # halfway through writing never leaves a half-written save file.
        temp_path = path + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
        os.replace(temp_path, path)
    except OSError as error:
        raise OSError("Could not save tasks to '" + file_name + "'") from error

    return len(store["tasks"])


def read_save_file(path):
    """
    Read the data file and return (list of task dictionaries, next free id).

    A missing file is not an error: it simply means there are no tasks yet.
    """
    file_name = os.path.basename(path)
    if not os.path.exists(path):
        return [], 1

    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except ValueError as error:
        # json.JSONDecodeError and UnicodeDecodeError are both ValueErrors.
        raise OSError(
            "The save file '" + file_name + "' is corrupted (not valid JSON)") from error
    except OSError as error:
        raise OSError("Could not read the save file '" + file_name + "'") from error

    format_message = "The save file '" + file_name + "' has an unexpected format"
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise OSError(format_message)
    next_id = data.get("next_id")
    if not validation.is_whole_number(next_id) or next_id < 1:
        raise OSError(format_message)

    seen_ids = []
    for record in data["tasks"]:
        if not isinstance(record, dict):
            raise OSError(format_message)
        task_id = record.get("id")
        if not validation.is_whole_number(task_id) or task_id < 1:
            raise OSError(format_message)
        if task_id in seen_ids:
            raise OSError("The save file '" + file_name + "' contains duplicate task ids")
        seen_ids.append(task_id)

    # Never hand out an id that is already in use, even if next_id is stale.
    for task_id in seen_ids:
        if task_id >= next_id:
            next_id = task_id + 1

    return data["tasks"], next_id


def load_store(store):
    """Replace store["tasks"] with the tasks in the data file; return the count."""
    path = require_data_file(store)
    file_name = os.path.basename(path)
    records, next_id = read_save_file(path)

    loaded = []
    for record in records:
        fields = {}
        for key in record:
            if key != "id":
                fields[key] = record[key]
        try:
            cleaned = validation.clean_task_data(fields)
        except ValueError as error:
            raise OSError("The save file '" + file_name
                          + "' contains an invalid task: " + str(error)) from error
        task = {"id": record["id"]}
        task.update(cleaned)
        loaded.append(task)

    # Only replace the current tasks once the whole file loaded successfully.
    store["tasks"] = loaded
    store["next_id"] = next_id
    return len(loaded)
