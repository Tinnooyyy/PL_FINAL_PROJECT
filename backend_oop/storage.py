"""
Saving and loading tasks as JSON (object-oriented backend).

The JsonTaskStorage object only knows about files and plain dictionaries.
Turning those dictionaries into Task objects is the TaskManager's job.
"""

import json
import os
from pathlib import Path

from .exceptions import TaskStorageError, TaskValidationError


class JsonTaskStorage:
    """Reads and writes the task list to one JSON file."""

    def __init__(self, file_path):
        """Remember which file to use; the file itself is not touched yet."""
        if not isinstance(file_path, (str, os.PathLike)) or str(file_path).strip() == "":
            raise TaskValidationError("Data file must be a file path")
        self._path = Path(file_path)

    @property
    def path(self):
        """The path of the save file."""
        return self._path

    def save(self, task_dicts, next_id):
        """Write the tasks and the next free id to the file."""
        data = {"next_id": next_id, "tasks": task_dicts}
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            # Write to a temporary file first and then swap it in, so a crash
            # halfway through writing never leaves a half-written save file.
            temp_path = self._path.with_name(self._path.name + ".tmp")
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
            temp_path.replace(self._path)
        except OSError as error:
            raise TaskStorageError(
                f"Could not save tasks to '{self._path.name}'") from error

    def load(self):
        """
        Read the file and return (list of task dictionaries, next free id).

        A missing file is not an error: it simply means there are no tasks yet.
        """
        if not self._path.exists():
            return [], 1

        try:
            with self._path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except ValueError as error:
            # json.JSONDecodeError and UnicodeDecodeError are both ValueErrors.
            raise TaskStorageError(
                f"The save file '{self._path.name}' is corrupted (not valid JSON)") from error
        except OSError as error:
            raise TaskStorageError(
                f"Could not read the save file '{self._path.name}'") from error

        return self._check_structure(data)

    def _check_structure(self, data):
        """Make sure the loaded JSON has the shape we wrote; return (records, next_id)."""
        format_error = TaskStorageError(
            f"The save file '{self._path.name}' has an unexpected format")

        if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
            raise format_error
        next_id = data.get("next_id")
        if not self._is_whole_number(next_id) or next_id < 1:
            raise format_error

        seen_ids = set()
        for record in data["tasks"]:
            if not isinstance(record, dict):
                raise format_error
            task_id = record.get("id")
            if not self._is_whole_number(task_id) or task_id < 1:
                raise format_error
            if task_id in seen_ids:
                raise TaskStorageError(
                    f"The save file '{self._path.name}' contains duplicate task ids")
            seen_ids.add(task_id)

        # Never hand out an id that is already in use, even if next_id is stale.
        if seen_ids:
            next_id = max(next_id, max(seen_ids) + 1)
        return data["tasks"], next_id

    @staticmethod
    def _is_whole_number(value):
        """Return True for ints but not for booleans (True/False are ints in Python)."""
        return isinstance(value, int) and not isinstance(value, bool)
