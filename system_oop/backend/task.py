"""
The Task class hierarchy.

    Task          a normal to-do item
    UrgentTask    a high-priority to-do item, which must have a due date

Both classes have a validate() method. Task.__init__ calls self.validate(),
and Python looks that method up on the actual object. So when an UrgentTask is
created, its own stricter validate() runs instead of the base one. This is
polymorphism: the same call behaves differently depending on the object's class.
"""

from datetime import datetime

from .constants import (
    CATEGORIES,
    DEFAULT_PRIORITY,
    DEFAULT_STATUS,
    DUE_DATE_FORMAT,
    EDITABLE_FIELDS,
    MAX_DESCRIPTION_LENGTH,
    MAX_TITLE_LENGTH,
    PRIORITIES,
    STATUSES,
)
from .exceptions import TaskValidationError


class Task:
    """A single to-do item with a title, description, due date, priority, status and category."""

    def __init__(self, task_id, title="", description="", due_date="",
                 priority=DEFAULT_PRIORITY, status=DEFAULT_STATUS, category=""):
        """Create a task from raw values, cleaning and validating them."""
        # The leading underscore marks these attributes as "protected":
        # other code should read them through the properties below and change
        # them only through methods like mark_complete().
        self._id = task_id
        self._title = self._clean_text(title, "title")
        self._description = self._clean_text(description, "description")
        self._due_date = self._clean_text(due_date, "due_date")
        self._priority = self._clean_text(priority, "priority").lower()
        self._status = self._clean_text(status, "status").lower()
        self._category = self._clean_text(category, "category").lower()
        self.validate()

    # ----- Read-only properties (encapsulation) -----------------------------

    @property
    def id(self):
        """The unique number of this task."""
        return self._id

    @property
    def title(self):
        """The task title."""
        return self._title

    @property
    def description(self):
        """The task description ("" if there is none)."""
        return self._description

    @property
    def due_date(self):
        """The due date as "YYYY-MM-DD HH:MM", or "" if there is none."""
        return self._due_date

    @property
    def due_datetime(self):
        """The due date as a datetime object (used for sorting), or None."""
        if self._due_date == "":
            return None
        return self._parse_due_date(self._due_date)

    @property
    def priority(self):
        """One of "low", "medium" or "high"."""
        return self._priority

    @property
    def status(self):
        """One of "pending", "in_progress" or "completed"."""
        return self._status

    @property
    def category(self):
        """One of "personal", "academic" or "work"."""
        return self._category

    # ----- Behaviour ---------------------------------------------------------

    def validate(self):
        """Check the rules every task must follow; raise TaskValidationError if one fails."""
        if self._title == "":
            raise TaskValidationError("Title is required")
        if len(self._title) > MAX_TITLE_LENGTH:
            raise TaskValidationError(
                f"Title must be at most {MAX_TITLE_LENGTH} characters")
        if len(self._description) > MAX_DESCRIPTION_LENGTH:
            raise TaskValidationError(
                f"Description must be at most {MAX_DESCRIPTION_LENGTH} characters")
        if self._due_date != "" and self._parse_due_date(self._due_date) is None:
            raise TaskValidationError(
                "Due date must be a real date and time in YYYY-MM-DD HH:MM format")
        if self._priority not in PRIORITIES:
            raise TaskValidationError(
                "Priority must be one of: " + ", ".join(PRIORITIES))
        if self._status not in STATUSES:
            raise TaskValidationError(
                "Status must be one of: " + ", ".join(STATUSES))
        if self._category == "":
            raise TaskValidationError("Category is required")
        if self._category not in CATEGORIES:
            raise TaskValidationError(
                "Category must be one of: " + ", ".join(CATEGORIES))

    def mark_complete(self):
        """Change the status to "completed"; a task can only be completed once."""
        if self._status == "completed":
            raise TaskValidationError(f"Task {self._id} is already completed")
        self._status = "completed"

    def matches_keyword(self, keyword):
        """Return True if the lowercase keyword appears in the title or description."""
        return keyword in self._title.lower() or keyword in self._description.lower()

    def to_dict(self):
        """Convert the task to the plain dictionary format defined in the contract."""
        return {
            "id": self._id,
            "title": self._title,
            "description": self._description,
            "due_date": self._due_date,
            "priority": self._priority,
            "status": self._status,
            "category": self._category,
        }

    def __repr__(self):
        """Show the real class name, e.g. UrgentTask(id=3, title='Pay rent')."""
        return f"{type(self).__name__}(id={self._id}, title={self._title!r})"

    # ----- Helpers -----------------------------------------------------------

    @staticmethod
    def _clean_text(value, field_name):
        """Return the value with surrounding spaces removed; None becomes ""."""
        if value is None:
            return ""
        if not isinstance(value, str):
            label = field_name.replace("_", " ").capitalize()
            raise TaskValidationError(f"{label} must be text")
        return value.strip()

    @staticmethod
    def _parse_due_date(text):
        """Return a datetime for a valid "YYYY-MM-DD HH:MM" text, otherwise None."""
        try:
            # strptime rejects impossible dates (2026-02-30), impossible times
            # (25:00) and text without a time part.
            parsed = datetime.strptime(text, DUE_DATE_FORMAT)
        except ValueError:
            return None
        # strptime also accepts "2026-1-5 9:30", so insist on the zero-padded
        # form; that way every stored due date looks the same.
        if parsed.strftime(DUE_DATE_FORMAT) != text:
            return None
        return parsed


class UrgentTask(Task):
    """A high-priority task. It follows every Task rule, plus: it must have a due date."""

    def validate(self):
        """Run the normal checks first, then the extra rule for urgent tasks."""
        super().validate()
        if self._due_date == "":
            raise TaskValidationError("High-priority tasks must have a due date")


def create_task(task_id, task_data):
    """
    Build the right kind of task object from a dictionary of fields.

    Returns an UrgentTask when the priority is "high", otherwise a Task.
    """
    if not isinstance(task_data, dict):
        raise TaskValidationError("Task data must be an object")

    unknown_fields = sorted(str(key) for key in task_data if key not in EDITABLE_FIELDS)
    if unknown_fields:
        raise TaskValidationError("Unknown field(s): " + ", ".join(unknown_fields))

    priority = task_data.get("priority", DEFAULT_PRIORITY)
    is_high = isinstance(priority, str) and priority.strip().lower() == "high"
    task_class = UrgentTask if is_high else Task

    # **task_data unpacks the dictionary into keyword arguments,
    # e.g. title="Buy milk", priority="low".
    return task_class(task_id, **task_data)
