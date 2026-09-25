"""
The TaskManager class: owns the list of Task objects and every operation on it.
"""

from .constants import PRIORITIES, PRIORITY_RANK, SORT_FIELDS, STATUSES
from .exceptions import (
    TaskNotFoundError,
    TaskStorageError,
    TaskValidationError,
)
from .task import create_task


class TaskManager:
    """Keeps the tasks in memory, changes them, queries them and saves them."""

    def __init__(self, storage=None):
        """Start with no tasks. `storage` is a JsonTaskStorage (or None)."""
        self._tasks = []        # list of Task / UrgentTask objects, in id order
        self._next_id = 1       # the id the next new task will get
        self._storage = storage

    # ----- Create, read, update, delete ------------------------------------

    def add_task(self, task_data):
        """Create a task from a dictionary, store it, save, and return it."""
        task = create_task(self._next_id, task_data)
        self._tasks.append(task)
        self._next_id += 1
        self._autosave()
        return task

    def get_all_tasks(self):
        """Return a new list holding every task (so callers cannot change ours)."""
        return list(self._tasks)

    def get_task(self, task_id):
        """Return the task with this id."""
        return self._tasks[self._find_index(task_id)]

    def update_task(self, task_id, changes):
        """Apply a dictionary of changes to a task, save, and return the new task."""
        index = self._find_index(task_id)
        if not isinstance(changes, dict):
            raise TaskValidationError("Changes must be an object")
        if not changes:
            raise TaskValidationError("No changes were provided")

        merged = self._tasks[index].to_dict()
        del merged["id"]
        merged.update(changes)

        # Build a brand-new object instead of editing the old one. If the
        # priority changed to or from "high", the task must become a different
        # class (UrgentTask <-> Task), and the old task stays untouched if
        # the new data turns out to be invalid.
        updated = create_task(task_id, merged)
        self._tasks[index] = updated
        self._autosave()
        return updated

    def complete_task(self, task_id):
        """Mark a task as completed, save, and return it."""
        task = self.get_task(task_id)
        task.mark_complete()
        self._autosave()
        return task

    def delete_task(self, task_id):
        """Remove a task, save, and return the removed task."""
        index = self._find_index(task_id)
        removed = self._tasks.pop(index)
        self._autosave()
        return removed

    # ----- Queries ---------------------------------------------------------

    def search_tasks(self, keyword):
        """Return tasks whose title or description contains the keyword."""
        return self._search(self._tasks, keyword)

    def filter_tasks(self, status=None, priority=None):
        """Return tasks with the given status and/or priority."""
        return self._filter(self._tasks, status, priority)

    def sort_tasks(self, sort_by, descending=False):
        """Return all tasks sorted by "due_date" or "priority"."""
        return self._sort(self._tasks, sort_by, descending)

    def query_tasks(self, keyword=None, status=None, priority=None,
                    sort_by=None, descending=False):
        """Search, then filter, then sort. Blank arguments skip that step."""
        results = self._search(self._tasks, keyword)
        results = self._filter(results, status, priority)
        if not self._is_blank(sort_by):
            results = self._sort(results, sort_by, descending)
        return results

    # ----- Saving and loading ----------------------------------------------

    def save(self):
        """Write every task to the save file; return how many were saved."""
        storage = self._require_storage()
        storage.save([task.to_dict() for task in self._tasks], self._next_id)
        return len(self._tasks)

    def load(self):
        """Replace the tasks in memory with those in the save file; return the count."""
        storage = self._require_storage()
        records, next_id = storage.load()

        loaded = []
        for record in records:
            fields = dict(record)
            task_id = fields.pop("id")
            try:
                loaded.append(create_task(task_id, fields))
            except TaskValidationError as error:
                raise TaskStorageError(
                    f"The save file '{storage.path.name}' contains an invalid task: {error}"
                ) from error

        # Only replace the current tasks once the whole file loaded successfully.
        self._tasks = loaded
        self._next_id = next_id
        return len(loaded)

    # ----- Private helpers -------------------------------------------------

    def _autosave(self):
        """Save after every change so no work is lost."""
        self.save()

    def _require_storage(self):
        """Return the storage object, or fail if none has been configured."""
        if self._storage is None:
            raise TaskStorageError("No data file has been configured")
        return self._storage

    def _find_index(self, task_id):
        """Return the list position of the task with this id."""
        if isinstance(task_id, bool) or not isinstance(task_id, int):
            raise TaskValidationError("Task id must be a whole number")
        for index, task in enumerate(self._tasks):
            if task.id == task_id:
                return index
        raise TaskNotFoundError(task_id)

    def _search(self, tasks, keyword):
        """Return the tasks from `tasks` that match the keyword."""
        keyword = self._clean_keyword(keyword)
        if keyword == "":
            return list(tasks)
        return [task for task in tasks if task.matches_keyword(keyword)]

    def _filter(self, tasks, status, priority):
        """Return the tasks from `tasks` that match the status and priority."""
        status = self._optional_choice(status, STATUSES, "Status")
        priority = self._optional_choice(priority, PRIORITIES, "Priority")
        # filter() is a higher-order function: it calls the lambda on every
        # task and keeps the ones for which it returns True.
        return list(filter(
            lambda task: (status is None or task.status == status)
            and (priority is None or task.priority == priority),
            tasks,
        ))

    def _sort(self, tasks, sort_by, descending):
        """Return a sorted copy of `tasks`. Ties are broken by id."""
        sort_by = self._required_choice(sort_by, SORT_FIELDS, "Sort field")
        descending = self._parse_bool(descending, "Descending")

        # Sort by id first. Python's sort is stable (even with reverse=True),
        # so tasks that tie in the second sort keep this id order.
        by_id = sorted(tasks, key=lambda task: task.id)

        if sort_by == "priority":
            return sorted(by_id, key=lambda task: PRIORITY_RANK[task.priority],
                          reverse=descending)

        # Tasks without a due date always go last, whichever direction we sort.
        dated = [task for task in by_id if task.due_date != ""]
        undated = [task for task in by_id if task.due_date == ""]
        # "YYYY-MM-DD" text sorts in the same order as the real dates.
        return sorted(dated, key=lambda task: task.due_date, reverse=descending) + undated

    @staticmethod
    def _is_blank(value):
        """Return True for None or text that is empty after trimming."""
        return value is None or (isinstance(value, str) and value.strip() == "")

    @staticmethod
    def _clean_keyword(keyword):
        """Return the keyword in lowercase without surrounding spaces."""
        if keyword is None:
            return ""
        if not isinstance(keyword, str):
            raise TaskValidationError("Keyword must be text")
        return keyword.strip().lower()

    @classmethod
    def _optional_choice(cls, value, allowed, label):
        """Return None for a blank value, otherwise the checked lowercase value."""
        if cls._is_blank(value):
            return None
        return cls._required_choice(value, allowed, label)

    @staticmethod
    def _required_choice(value, allowed, label):
        """Return the value in lowercase if it is one of `allowed`."""
        if not isinstance(value, str) or value.strip().lower() not in allowed:
            raise TaskValidationError(f"{label} must be one of: " + ", ".join(allowed))
        return value.strip().lower()

    @staticmethod
    def _parse_bool(value, label):
        """Accept True/False or the text "true"/"false"."""
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in ("true", "false"):
            return value.strip().lower() == "true"
        raise TaskValidationError(f"{label} must be true or false")
