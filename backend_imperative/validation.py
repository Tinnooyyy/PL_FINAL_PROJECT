"""
Validation procedures for the imperative backend.

Each function checks one kind of input. When the input is invalid it raises a
built-in ValueError with a message that can be shown to the user.
"""

import os
from datetime import datetime

from .constants import (
    DATE_FORMAT,
    DEFAULT_PRIORITY,
    DEFAULT_STATUS,
    EDITABLE_FIELDS,
    MAX_DESCRIPTION_LENGTH,
    MAX_TITLE_LENGTH,
    PRIORITIES,
    STATUSES,
)


def make_label(field_name):
    """Turn a field name like "due_date" into a label like "Due date"."""
    return field_name.replace("_", " ").capitalize()


def clean_text(value, field_name):
    """Return the value with surrounding spaces removed; None becomes ""."""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(make_label(field_name) + " must be text")
    return value.strip()


def is_valid_date(text):
    """Return True if text is a real calendar date written as YYYY-MM-DD."""
    try:
        parsed = datetime.strptime(text, DATE_FORMAT)
    except ValueError:
        return False
    # strptime also accepts "2026-1-5", so insist on the zero-padded form.
    return parsed.strftime(DATE_FORMAT) == text


def is_whole_number(value):
    """Return True for ints but not for booleans (True/False are ints in Python)."""
    return isinstance(value, int) and not isinstance(value, bool)


def is_blank(value):
    """Return True for None or text that is empty after trimming."""
    return value is None or (isinstance(value, str) and value.strip() == "")


def check_task_id(task_id):
    """Raise ValueError unless task_id is a whole number."""
    if not is_whole_number(task_id):
        raise ValueError("Task id must be a whole number")


def check_data_file(data_file):
    """Raise ValueError unless data_file looks like a file path."""
    if not isinstance(data_file, (str, os.PathLike)) or str(data_file).strip() == "":
        raise ValueError("Data file must be a file path")


def clean_task_data(task_data):
    """
    Check a dictionary of task fields and return a cleaned copy.

    Missing fields get their default values. The returned dictionary has
    exactly the keys title, description, due_date, priority and status.
    """
    if not isinstance(task_data, dict):
        raise ValueError("Task data must be an object")

    unknown_fields = []
    for key in task_data:
        if key not in EDITABLE_FIELDS:
            unknown_fields.append(str(key))
    if len(unknown_fields) > 0:
        unknown_fields.sort()
        raise ValueError("Unknown field(s): " + ", ".join(unknown_fields))

    # Start from the defaults, then copy in whatever the caller gave us.
    task = {
        "title": "",
        "description": "",
        "due_date": "",
        "priority": DEFAULT_PRIORITY,
        "status": DEFAULT_STATUS,
    }
    for field in EDITABLE_FIELDS:
        if field in task_data:
            task[field] = task_data[field]
        task[field] = clean_text(task[field], field)

    task["priority"] = task["priority"].lower()
    task["status"] = task["status"].lower()

    check_task_rules(task)
    return task


def check_task_rules(task):
    """Raise ValueError if a cleaned task breaks any business rule."""
    if task["title"] == "":
        raise ValueError("Title is required")
    if len(task["title"]) > MAX_TITLE_LENGTH:
        raise ValueError("Title must be at most " + str(MAX_TITLE_LENGTH) + " characters")
    if len(task["description"]) > MAX_DESCRIPTION_LENGTH:
        raise ValueError(
            "Description must be at most " + str(MAX_DESCRIPTION_LENGTH) + " characters")
    if task["due_date"] != "" and not is_valid_date(task["due_date"]):
        raise ValueError("Due date must be a real date in YYYY-MM-DD format")
    if task["priority"] not in PRIORITIES:
        raise ValueError("Priority must be one of: " + ", ".join(PRIORITIES))
    if task["status"] not in STATUSES:
        raise ValueError("Status must be one of: " + ", ".join(STATUSES))
    # The rule for urgent work: a high-priority task needs a deadline.
    if task["priority"] == "high" and task["due_date"] == "":
        raise ValueError("High-priority tasks must have a due date")


def clean_keyword(keyword):
    """Return the search keyword in lowercase without surrounding spaces."""
    if keyword is None:
        return ""
    if not isinstance(keyword, str):
        raise ValueError("Keyword must be text")
    return keyword.strip().lower()


def clean_required_choice(value, allowed, label):
    """Return the value in lowercase if it is one of `allowed`."""
    if not isinstance(value, str) or value.strip().lower() not in allowed:
        raise ValueError(label + " must be one of: " + ", ".join(allowed))
    return value.strip().lower()


def clean_optional_choice(value, allowed, label):
    """Return None for a blank value, otherwise the checked lowercase value."""
    if is_blank(value):
        return None
    return clean_required_choice(value, allowed, label)


def parse_bool(value, label):
    """Accept True/False or the text "true"/"false"."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        text = value.strip().lower()
        if text == "true":
            return True
        if text == "false":
            return False
    raise ValueError(label + " must be true or false")
