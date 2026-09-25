"""
Fixed values used by the object-oriented backend.

Tuples are used because these values never change while the program runs.
"""

PRIORITIES = ("low", "medium", "high")
STATUSES = ("pending", "in_progress", "completed")
SORT_FIELDS = ("due_date", "priority")

# Lets us compare priorities as numbers: low < medium < high.
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}

# The only fields a caller is allowed to set. The id is always assigned by us.
EDITABLE_FIELDS = ("title", "description", "due_date", "priority", "status")

DEFAULT_PRIORITY = "medium"
DEFAULT_STATUS = "pending"

DATE_FORMAT = "%Y-%m-%d"
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
