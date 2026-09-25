"""
Fixed values used by the imperative backend.

Tuples are used because these values never change while the program runs.
"""

PRIORITIES = ("low", "medium", "high")
STATUSES = ("pending", "in_progress", "completed")
CATEGORIES = ("personal", "academic", "work")
SORT_FIELDS = ("due_date", "priority")

# Lets us compare priorities as numbers: low < medium < high.
PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}

# The only fields a caller is allowed to set. The id is always assigned by us.
EDITABLE_FIELDS = ("title", "description", "due_date", "priority", "status",
                   "category")

# Category has no default on purpose: the caller must always choose one.
DEFAULT_PRIORITY = "medium"
DEFAULT_STATUS = "pending"

# Due dates are stored as text like "2026-10-05 14:30" (24-hour clock).
DUE_DATE_FORMAT = "%Y-%m-%d %H:%M"
MAX_TITLE_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 500
