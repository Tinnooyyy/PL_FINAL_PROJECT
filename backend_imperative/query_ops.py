"""
Search, filter and sort procedures (imperative backend).

These use explicit loops and if-statements. Sorting is done with a
hand-written merge sort, which is recursive: it sorts a list by splitting it
in half, sorting each half the same way, and merging the two sorted halves.
"""

from . import validation
from .constants import CATEGORIES, PRIORITIES, PRIORITY_RANK, SORT_FIELDS, STATUSES


def search_tasks(tasks, keyword):
    """Return the tasks whose title or description contains the keyword."""
    keyword = validation.clean_keyword(keyword)
    results = []
    for task in tasks:
        if keyword == "":
            results.append(task)
        elif keyword in task["title"].lower() or keyword in task["description"].lower():
            results.append(task)
    return results


def filter_tasks(tasks, status=None, priority=None, category=None):
    """Return the tasks that match the status, priority and/or category (None = any)."""
    status = validation.clean_optional_choice(status, STATUSES, "Status")
    priority = validation.clean_optional_choice(priority, PRIORITIES, "Priority")
    category = validation.clean_optional_choice(category, CATEGORIES, "Category")

    results = []
    for task in tasks:
        if status is not None and task["status"] != status:
            continue
        if priority is not None and task["priority"] != priority:
            continue
        if category is not None and task["category"] != category:
            continue
        results.append(task)
    return results


def compare_tasks(first, second, sort_by, descending):
    """
    Compare two tasks for sorting.

    Returns a negative number if `first` should come before `second`,
    a positive number if it should come after. Ties are broken by id.
    """
    if sort_by == "priority":
        difference = PRIORITY_RANK[first["priority"]] - PRIORITY_RANK[second["priority"]]
    else:
        # Turn the text into datetime objects so the full date AND time is
        # compared (None means "no due date").
        first_due = validation.parse_due_date(first["due_date"])
        second_due = validation.parse_due_date(second["due_date"])
        # Tasks without a due date always go last, whichever direction we sort.
        if first_due is None and second_due is not None:
            return 1
        if first_due is not None and second_due is None:
            return -1
        if first_due is None or first_due == second_due:
            difference = 0
        elif first_due < second_due:
            difference = -1
        else:
            difference = 1

    if descending:
        difference = -difference
    if difference == 0:
        difference = first["id"] - second["id"]
    return difference


def merge_sort(items, compare):
    """
    Return a new sorted list (recursive merge sort).

    `compare` is a function passed in as a parameter (a higher-order function):
    compare(a, b) returns a negative number when a should come first.
    """
    # Base case: a list with 0 or 1 items is already sorted.
    if len(items) <= 1:
        return list(items)

    middle = len(items) // 2
    left = merge_sort(items[:middle], compare)    # recursive call
    right = merge_sort(items[middle:], compare)   # recursive call
    return merge(left, right, compare)


def merge(left, right, compare):
    """Combine two sorted lists into one sorted list."""
    merged = []
    left_index = 0
    right_index = 0

    while left_index < len(left) and right_index < len(right):
        if compare(left[left_index], right[right_index]) <= 0:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1

    # One of the lists is used up; copy whatever is left of the other.
    while left_index < len(left):
        merged.append(left[left_index])
        left_index += 1
    while right_index < len(right):
        merged.append(right[right_index])
        right_index += 1

    return merged


def sort_tasks(tasks, sort_by, descending=False):
    """Return the tasks sorted by "due_date" or "priority"."""
    sort_by = validation.clean_required_choice(sort_by, SORT_FIELDS, "Sort field")
    descending = validation.parse_bool(descending, "Descending")
    # The lambda "remembers" sort_by and descending and passes them on.
    return merge_sort(
        tasks, lambda first, second: compare_tasks(first, second, sort_by, descending))


def query_tasks(tasks, keyword=None, status=None, priority=None, category=None,
                sort_by=None, descending=False):
    """Search, then filter, then sort. Blank arguments skip that step."""
    results = search_tasks(tasks, keyword)
    results = filter_tasks(results, status, priority, category)
    if not validation.is_blank(sort_by):
        results = sort_tasks(results, sort_by, descending)
    return results
