"""
Custom exception classes for the object-oriented backend.

Each class also inherits from a built-in exception type (ValueError, KeyError
or OSError). That way code outside this backend, such as the API, can handle
errors from both backends the same way, while code inside this backend can
still catch the more specific custom types.
"""


class TaskError(Exception):
    """Base class for every error raised by the OOP backend."""

    def __init__(self, message):
        """Store a human-readable message describing what went wrong."""
        super().__init__(message)
        self.message = message

    def __str__(self):
        """Return the plain message (KeyError would otherwise add quotes)."""
        return self.message


class TaskValidationError(TaskError, ValueError):
    """Raised when task data or a query argument is invalid."""


class TaskNotFoundError(TaskError, KeyError):
    """Raised when no task has the requested id."""

    def __init__(self, task_id):
        """Build the message from the id that could not be found."""
        super().__init__(f"Task with id {task_id} was not found")
        self.task_id = task_id


class TaskStorageError(TaskError, OSError):
    """Raised when the save file cannot be read, written or understood."""
