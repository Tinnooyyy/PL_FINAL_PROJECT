"""
The ONE set of test cases that is run against BOTH backends.

SharedBackendTests is a "mixin": it is not a TestCase by itself, so unittest
does not run it directly. test_oop.py and test_imperative.py each combine it
with unittest.TestCase and set `backend` to their backend's service module.

The tests call the backends directly (not through the servers).
"""

import json
import os
import sys
import tempfile

# Make the project root importable no matter where the tests are started from.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from contract.backend_contract import TASK_FIELDS  # noqa: E402

DUE_DATE_ERROR = "Due date must be a real date and time in YYYY-MM-DD HH:MM format"
CATEGORY_ERROR = "Category must be one of: personal, academic, work"


class SharedBackendTests:
    """Test cases every backend must pass. Subclasses set `backend`."""

    backend = None  # the backend's service module, set by the subclass

    # ----- Setup and helpers -------------------------------------------------

    def setUp(self):
        """Give every test its own empty save file in a temporary folder."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_file = os.path.join(self.temp_dir.name, "tasks.json")
        self.backend.configure(self.data_file)

    def tearDown(self):
        """Delete the temporary folder."""
        self.temp_dir.cleanup()

    def add(self, **fields):
        """
        Shortcut: add a task using keyword arguments as the task data.

        Uses category "personal" unless the test gives one, because every
        task needs a category. Tests about a MISSING category call
        self.backend.add_task directly instead.
        """
        fields.setdefault("category", "personal")
        return self.backend.add_task(fields)

    def add_sample_tasks(self):
        """Add four tasks that the search/filter/sort tests use."""
        self.add(title="Buy milk", priority="low", due_date="2026-10-05 09:00",
                 category="personal")
        self.add(title="Pay rent", description="Send to landlord",
                 priority="high", due_date="2026-10-01 18:00", category="personal")
        self.add(title="Read book", description="Chapter about MILK",
                 category="academic")
        self.add(title="Plan trip", priority="medium", due_date="2026-10-01 18:00",
                 status="in_progress", category="work")

    def ids(self, tasks):
        """Return just the ids of a list of tasks."""
        return [task["id"] for task in tasks]

    def assert_error(self, error_type, message, function, *args):
        """Check that function(*args) raises error_type with exactly this message."""
        with self.assertRaises(error_type) as context:
            function(*args)
        self.assertEqual(context.exception.args[0], message)

    def write_save_file(self, content):
        """Overwrite the save file with raw text (used to test bad files)."""
        with open(self.data_file, "w", encoding="utf-8") as file:
            file.write(content)

    def saved_task(self, **fields):
        """A complete task record as it appears in a save file."""
        record = {"id": 1, "title": "A", "description": "", "due_date": "",
                  "priority": "low", "status": "pending", "category": "personal"}
        record.update(fields)
        return record

    # ----- Adding tasks (normal cases) -------------------------------------------

    def test_add_task_uses_defaults(self):
        task = self.add(title="Buy milk")
        self.assertEqual(task, {
            "id": 1, "title": "Buy milk", "description": "", "due_date": "",
            "priority": "medium", "status": "pending", "category": "personal",
        })

    def test_add_task_returns_fields_in_contract_order(self):
        task = self.add(title="Buy milk")
        self.assertEqual(list(task.keys()), TASK_FIELDS)

    def test_add_task_trims_text_and_lowercases_choices(self):
        task = self.add(title="  Buy milk  ", description=" 2 litres ",
                        priority="LOW", status="In_Progress", category=" WORK ")
        self.assertEqual(task["title"], "Buy milk")
        self.assertEqual(task["description"], "2 litres")
        self.assertEqual(task["priority"], "low")
        self.assertEqual(task["status"], "in_progress")
        self.assertEqual(task["category"], "work")

    def test_add_task_with_all_fields(self):
        task = self.add(title="Pay rent", description="Landlord",
                        due_date="2026-10-01 17:30", priority="high",
                        status="pending", category="personal")
        self.assertEqual(task["due_date"], "2026-10-01 17:30")
        self.assertEqual(task["priority"], "high")

    def test_ids_increase_by_one(self):
        first = self.add(title="A")
        second = self.add(title="B")
        self.assertEqual((first["id"], second["id"]), (1, 2))

    def test_title_of_exactly_100_characters_is_allowed(self):
        task = self.add(title="x" * 100)
        self.assertEqual(len(task["title"]), 100)

    # ----- Adding tasks (error cases) --------------------------------------------

    def test_empty_title_is_rejected(self):
        self.assert_error(ValueError, "Title is required",
                          self.backend.add_task, {"title": "", "category": "work"})

    def test_whitespace_only_title_is_rejected(self):
        self.assert_error(ValueError, "Title is required",
                          self.backend.add_task, {"title": "   ", "category": "work"})

    def test_missing_title_is_rejected(self):
        self.assert_error(ValueError, "Title is required",
                          self.backend.add_task, {"priority": "low", "category": "work"})

    def test_title_longer_than_100_characters_is_rejected(self):
        self.assert_error(ValueError, "Title must be at most 100 characters",
                          self.backend.add_task, {"title": "x" * 101, "category": "work"})

    def test_description_longer_than_500_characters_is_rejected(self):
        self.assert_error(ValueError, "Description must be at most 500 characters",
                          self.backend.add_task,
                          {"title": "A", "description": "x" * 501, "category": "work"})

    def test_title_that_is_not_text_is_rejected(self):
        self.assert_error(ValueError, "Title must be text",
                          self.backend.add_task, {"title": 42, "category": "work"})

    def test_invalid_priority_is_rejected(self):
        self.assert_error(ValueError, "Priority must be one of: low, medium, high",
                          self.backend.add_task,
                          {"title": "A", "priority": "urgent", "category": "work"})

    def test_invalid_status_is_rejected(self):
        self.assert_error(ValueError, "Status must be one of: pending, in_progress, completed",
                          self.backend.add_task,
                          {"title": "A", "status": "done", "category": "work"})

    def test_high_priority_without_due_date_is_rejected(self):
        self.assert_error(ValueError, "High-priority tasks must have a due date",
                          self.backend.add_task,
                          {"title": "A", "priority": "high", "category": "work"})

    def test_unknown_fields_are_rejected(self):
        self.assert_error(ValueError, "Unknown field(s): colour, id",
                          self.backend.add_task,
                          {"title": "A", "id": 5, "colour": "red", "category": "work"})

    def test_task_data_that_is_not_a_dictionary_is_rejected(self):
        self.assert_error(ValueError, "Task data must be an object",
                          self.backend.add_task, ["title", "A"])

    def test_failed_add_does_not_use_up_an_id(self):
        with self.assertRaises(ValueError):
            self.add(title="")
        self.assertEqual(self.add(title="A")["id"], 1)

    # ----- Category ------------------------------------------------------------

    def test_add_task_with_each_category(self):
        for category in ("personal", "academic", "work"):
            with self.subTest(category=category):
                task = self.add(title="A", category=category)
                self.assertEqual(task["category"], category)

    def test_invalid_category_is_rejected(self):
        self.assert_error(ValueError, CATEGORY_ERROR,
                          self.backend.add_task, {"title": "A", "category": "hobby"})

    def test_missing_category_is_rejected(self):
        self.assert_error(ValueError, "Category is required",
                          self.backend.add_task, {"title": "A"})

    def test_blank_category_is_rejected(self):
        self.assert_error(ValueError, "Category is required",
                          self.backend.add_task, {"title": "A", "category": "  "})

    def test_category_that_is_not_text_is_rejected(self):
        self.assert_error(ValueError, "Category must be text",
                          self.backend.add_task, {"title": "A", "category": 3})

    def test_update_category(self):
        self.add(title="A", category="personal")
        updated = self.backend.update_task(1, {"category": "Academic"})
        self.assertEqual(updated["category"], "academic")
        self.assertEqual(self.backend.get_task(1)["category"], "academic")

    def test_update_to_invalid_category_is_rejected_and_keeps_old_one(self):
        self.add(title="A", category="work")
        self.assert_error(ValueError, CATEGORY_ERROR,
                          self.backend.update_task, 1, {"category": "school"})
        self.assertEqual(self.backend.get_task(1)["category"], "work")

    def test_update_cannot_remove_the_category(self):
        self.add(title="A", category="work")
        self.assert_error(ValueError, "Category is required",
                          self.backend.update_task, 1, {"category": ""})

    # ----- Due date and time -----------------------------------------------------

    def test_valid_date_and_time_is_stored_unchanged(self):
        task = self.add(title="A", due_date="2026-10-05 14:30")
        self.assertEqual(task["due_date"], "2026-10-05 14:30")

    def test_midnight_and_last_minute_are_valid_times(self):
        self.assertEqual(self.add(title="A", due_date="2026-10-05 00:00")["due_date"],
                         "2026-10-05 00:00")
        self.assertEqual(self.add(title="B", due_date="2026-10-05 23:59")["due_date"],
                         "2026-10-05 23:59")

    def test_leap_day_is_a_valid_date(self):
        task = self.add(title="Leap", due_date="2028-02-29 12:00")
        self.assertEqual(task["due_date"], "2028-02-29 12:00")

    def test_invalid_hour_is_rejected(self):
        self.assert_error(ValueError, DUE_DATE_ERROR, self.backend.add_task,
                          {"title": "A", "due_date": "2026-10-05 25:00", "category": "work"})

    def test_invalid_minute_is_rejected(self):
        self.assert_error(ValueError, DUE_DATE_ERROR, self.backend.add_task,
                          {"title": "A", "due_date": "2026-10-05 10:60", "category": "work"})

    def test_date_without_time_is_rejected(self):
        self.assert_error(ValueError, DUE_DATE_ERROR, self.backend.add_task,
                          {"title": "A", "due_date": "2026-10-05", "category": "work"})

    def test_impossible_date_with_valid_time_is_rejected(self):
        self.assert_error(ValueError, DUE_DATE_ERROR, self.backend.add_task,
                          {"title": "A", "due_date": "2026-02-30 10:00", "category": "work"})

    def test_wrongly_formatted_date_is_rejected(self):
        self.assert_error(ValueError, DUE_DATE_ERROR, self.backend.add_task,
                          {"title": "A", "due_date": "05/10/2026 10:00", "category": "work"})

    def test_date_and_time_without_leading_zeros_is_rejected(self):
        self.assert_error(ValueError, DUE_DATE_ERROR, self.backend.add_task,
                          {"title": "A", "due_date": "2026-9-5 9:30", "category": "work"})

    def test_seconds_are_rejected(self):
        self.assert_error(ValueError, DUE_DATE_ERROR, self.backend.add_task,
                          {"title": "A", "due_date": "2026-10-05 10:00:00", "category": "work"})

    def test_12_hour_clock_is_rejected(self):
        self.assert_error(ValueError, DUE_DATE_ERROR, self.backend.add_task,
                          {"title": "A", "due_date": "2026-10-05 2:30 PM", "category": "work"})

    def test_high_priority_accepts_date_with_time(self):
        task = self.add(title="A", priority="high", due_date="2026-10-05 08:00")
        self.assertEqual(task["priority"], "high")

    # ----- Reading tasks ---------------------------------------------------------

    def test_get_all_tasks_returns_tasks_in_the_order_added(self):
        self.add(title="A")
        self.add(title="B")
        self.assertEqual([task["title"] for task in self.backend.get_all_tasks()], ["A", "B"])

    def test_get_all_tasks_is_empty_at_start(self):
        self.assertEqual(self.backend.get_all_tasks(), [])

    def test_get_task_by_id(self):
        self.add(title="A")
        self.add(title="B")
        self.assertEqual(self.backend.get_task(2)["title"], "B")

    def test_get_missing_task_raises_key_error(self):
        self.assert_error(KeyError, "Task with id 7 was not found", self.backend.get_task, 7)

    def test_task_id_that_is_not_a_whole_number_is_rejected(self):
        self.assert_error(ValueError, "Task id must be a whole number",
                          self.backend.get_task, "1")

    def test_returned_tasks_are_copies(self):
        self.add(title="A")
        returned = self.backend.get_all_tasks()
        returned[0]["title"] = "Changed from outside"
        self.assertEqual(self.backend.get_task(1)["title"], "A")

    # ----- Updating tasks ------------------------------------------------------

    def test_update_changes_only_the_given_fields(self):
        self.add(title="A", description="old", category="academic")
        updated = self.backend.update_task(1, {"description": "new"})
        self.assertEqual(updated["title"], "A")
        self.assertEqual(updated["description"], "new")
        self.assertEqual(updated["category"], "academic")
        self.assertEqual(self.backend.get_task(1), updated)

    def test_update_to_high_priority_with_due_date(self):
        self.add(title="A")
        updated = self.backend.update_task(
            1, {"priority": "high", "due_date": "2026-12-01 09:15"})
        self.assertEqual(updated["priority"], "high")

    def test_update_from_high_priority_allows_removing_due_date(self):
        self.add(title="A", priority="high", due_date="2026-12-01 09:15")
        updated = self.backend.update_task(1, {"priority": "low", "due_date": ""})
        self.assertEqual((updated["priority"], updated["due_date"]), ("low", ""))

    def test_update_to_high_priority_without_due_date_is_rejected(self):
        self.add(title="A")
        self.assert_error(ValueError, "High-priority tasks must have a due date",
                          self.backend.update_task, 1, {"priority": "high"})

    def test_update_to_date_without_time_is_rejected(self):
        self.add(title="A", due_date="2026-10-05 10:00")
        self.assert_error(ValueError, DUE_DATE_ERROR,
                          self.backend.update_task, 1, {"due_date": "2026-10-06"})
        self.assertEqual(self.backend.get_task(1)["due_date"], "2026-10-05 10:00")

    def test_failed_update_leaves_task_unchanged(self):
        self.add(title="A")
        with self.assertRaises(ValueError):
            self.backend.update_task(1, {"title": "B", "due_date": "not a date"})
        self.assertEqual(self.backend.get_task(1)["title"], "A")

    def test_update_missing_task_raises_key_error(self):
        self.assert_error(KeyError, "Task with id 3 was not found",
                          self.backend.update_task, 3, {"title": "B"})

    def test_update_with_no_changes_is_rejected(self):
        self.add(title="A")
        self.assert_error(ValueError, "No changes were provided",
                          self.backend.update_task, 1, {})

    def test_update_with_changes_that_are_not_a_dictionary_is_rejected(self):
        self.add(title="A")
        self.assert_error(ValueError, "Changes must be an object",
                          self.backend.update_task, 1, "B")

    def test_update_cannot_change_the_id(self):
        self.add(title="A")
        self.assert_error(ValueError, "Unknown field(s): id",
                          self.backend.update_task, 1, {"id": 99})

    # ----- Completing tasks ----------------------------------------------------

    def test_complete_task_sets_status_to_completed(self):
        self.add(title="A")
        self.assertEqual(self.backend.complete_task(1)["status"], "completed")
        self.assertEqual(self.backend.get_task(1)["status"], "completed")

    def test_completing_twice_is_rejected(self):
        self.add(title="A")
        self.backend.complete_task(1)
        self.assert_error(ValueError, "Task 1 is already completed",
                          self.backend.complete_task, 1)

    def test_complete_missing_task_raises_key_error(self):
        self.assert_error(KeyError, "Task with id 5 was not found",
                          self.backend.complete_task, 5)

    # ----- Deleting tasks ------------------------------------------------------

    def test_delete_task_returns_and_removes_it(self):
        self.add(title="A")
        self.add(title="B")
        deleted = self.backend.delete_task(1)
        self.assertEqual(deleted["title"], "A")
        self.assertEqual(self.ids(self.backend.get_all_tasks()), [2])

    def test_delete_missing_task_raises_key_error(self):
        self.assert_error(KeyError, "Task with id 99 was not found",
                          self.backend.delete_task, 99)

    def test_ids_are_not_reused_after_delete(self):
        self.add(title="A")
        self.backend.delete_task(1)
        self.assertEqual(self.add(title="B")["id"], 2)

    # ----- Searching -----------------------------------------------------------

    def test_search_is_case_insensitive_and_checks_description(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.search_tasks("milk")), [1, 3])

    def test_search_trims_the_keyword(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.search_tasks("  RENT ")), [2])

    def test_blank_search_returns_all_tasks(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.search_tasks("")), [1, 2, 3, 4])

    def test_search_with_no_matches_returns_empty_list(self):
        self.add_sample_tasks()
        self.assertEqual(self.backend.search_tasks("zebra"), [])

    def test_search_keyword_that_is_not_text_is_rejected(self):
        self.assert_error(ValueError, "Keyword must be text", self.backend.search_tasks, 5)

    # ----- Filtering -----------------------------------------------------------

    def test_filter_by_status(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.filter_tasks(status="in_progress")), [4])

    def test_filter_by_priority(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.filter_tasks(priority="medium")), [3, 4])

    def test_filter_by_status_and_priority(self):
        self.add_sample_tasks()
        result = self.backend.filter_tasks(status="pending", priority="medium")
        self.assertEqual(self.ids(result), [3])

    def test_filter_by_category(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.filter_tasks(category="personal")), [1, 2])
        self.assertEqual(self.ids(self.backend.filter_tasks(category="academic")), [3])
        self.assertEqual(self.ids(self.backend.filter_tasks(category="WORK")), [4])

    def test_filter_by_category_combined_with_status_and_priority(self):
        self.add_sample_tasks()
        result = self.backend.filter_tasks("pending", "low", "personal")
        self.assertEqual(self.ids(result), [1])
        result = self.backend.filter_tasks(status="in_progress", category="personal")
        self.assertEqual(result, [])

    def test_filter_with_no_arguments_returns_all(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.filter_tasks()), [1, 2, 3, 4])

    def test_filter_with_invalid_status_is_rejected(self):
        self.assert_error(ValueError, "Status must be one of: pending, in_progress, completed",
                          self.backend.filter_tasks, "finished", None)

    def test_filter_with_invalid_category_is_rejected(self):
        self.assert_error(ValueError, CATEGORY_ERROR,
                          self.backend.filter_tasks, None, None, "hobby")

    # ----- Sorting -------------------------------------------------------------

    def test_sort_by_due_date_puts_undated_tasks_last(self):
        self.add_sample_tasks()
        # Tasks 2 and 4 are due at exactly the same moment, so they are ordered by id.
        self.assertEqual(self.ids(self.backend.sort_tasks("due_date")), [2, 4, 1, 3])

    def test_sort_by_due_date_descending_still_puts_undated_last(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.sort_tasks("due_date", True)), [1, 2, 4, 3])

    def test_sort_same_day_tasks_by_time(self):
        self.add(title="Evening", due_date="2026-10-05 18:45")
        self.add(title="Morning", due_date="2026-10-05 07:15")
        self.add(title="Noon", due_date="2026-10-05 12:00")
        self.assertEqual(self.ids(self.backend.sort_tasks("due_date")), [2, 3, 1])
        self.assertEqual(self.ids(self.backend.sort_tasks("due_date", True)), [1, 3, 2])

    def test_sort_time_does_not_beat_an_earlier_day(self):
        self.add(title="Late on day 1", due_date="2026-10-01 23:59")
        self.add(title="Early on day 2", due_date="2026-10-02 00:01")
        self.assertEqual(self.ids(self.backend.sort_tasks("due_date")), [1, 2])

    def test_sort_by_priority_ascending(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.sort_tasks("priority")), [1, 3, 4, 2])

    def test_sort_by_priority_descending_accepts_text_true(self):
        self.add_sample_tasks()
        self.assertEqual(self.ids(self.backend.sort_tasks("priority", "true")), [2, 3, 4, 1])

    def test_sort_does_not_change_stored_order(self):
        self.add_sample_tasks()
        self.backend.sort_tasks("priority")
        self.assertEqual(self.ids(self.backend.get_all_tasks()), [1, 2, 3, 4])

    def test_sort_by_unknown_field_is_rejected(self):
        self.assert_error(ValueError, "Sort field must be one of: due_date, priority",
                          self.backend.sort_tasks, "title")

    def test_sort_with_invalid_descending_value_is_rejected(self):
        self.assert_error(ValueError, "Descending must be true or false",
                          self.backend.sort_tasks, "priority", "maybe")

    # ----- Combined query --------------------------------------------------------

    def test_query_combines_search_filter_and_sort(self):
        self.add_sample_tasks()
        self.add(title="Buy bread", priority="high", due_date="2026-09-30 12:00")
        result = self.backend.query_tasks(keyword="buy", status="pending",
                                          sort_by="due_date")
        self.assertEqual(self.ids(result), [5, 1])

    def test_query_filters_by_category(self):
        self.add_sample_tasks()
        result = self.backend.query_tasks(keyword="", category="personal",
                                          sort_by="due_date")
        self.assertEqual(self.ids(result), [2, 1])

    def test_query_with_blank_arguments_returns_all(self):
        self.add_sample_tasks()
        result = self.backend.query_tasks("", "", "", "", "", "false")
        self.assertEqual(self.ids(result), [1, 2, 3, 4])

    # ----- Options ---------------------------------------------------------------

    def test_get_options(self):
        self.assertEqual(self.backend.get_options(), {
            "priorities": ["low", "medium", "high"],
            "statuses": ["pending", "in_progress", "completed"],
            "categories": ["personal", "academic", "work"],
            "sort_fields": ["due_date", "priority"],
            "defaults": {"priority": "medium", "status": "pending"},
        })

    # ----- Saving and loading --------------------------------------------------

    def test_changes_are_saved_automatically(self):
        self.add(title="A")
        self.add(title="B", category="work", due_date="2026-10-05 10:30")
        self.backend.complete_task(2)
        with open(self.data_file, encoding="utf-8") as file:
            saved = json.load(file)
        self.assertEqual([task["title"] for task in saved["tasks"]], ["A", "B"])
        self.assertEqual(saved["tasks"][1]["status"], "completed")
        self.assertEqual(saved["tasks"][1]["category"], "work")
        self.assertEqual(saved["tasks"][1]["due_date"], "2026-10-05 10:30")

    def test_tasks_persist_after_reconfiguring(self):
        self.add(title="A", priority="high", due_date="2026-11-11 11:11", category="work")
        self.add(title="B")
        before = self.backend.get_all_tasks()
        self.assertEqual(self.backend.configure(self.data_file), {"loaded": 2})
        self.assertEqual(self.backend.get_all_tasks(), before)

    def test_ids_continue_after_reloading(self):
        self.add(title="A")
        self.add(title="B")
        self.backend.delete_task(2)
        self.backend.configure(self.data_file)
        self.assertEqual(self.add(title="C")["id"], 3)

    def test_save_tasks_reports_count(self):
        self.add(title="A")
        self.assertEqual(self.backend.save_tasks(), {"saved": 1})

    def test_load_tasks_reads_changes_made_to_the_file(self):
        self.add(title="A")
        self.write_save_file(json.dumps({"next_id": 10, "tasks": [
            self.saved_task(id=4, title="From file", category="academic"),
        ]}))
        self.assertEqual(self.backend.load_tasks(), {"loaded": 1})
        self.assertEqual(self.backend.get_task(4)["title"], "From file")
        self.assertEqual(self.add(title="Next")["id"], 10)

    def test_missing_save_file_starts_empty(self):
        other_file = os.path.join(self.temp_dir.name, "does_not_exist.json")
        self.assertEqual(self.backend.configure(other_file), {"loaded": 0})
        self.assertEqual(self.backend.get_all_tasks(), [])

    def test_corrupted_save_file_raises_os_error(self):
        self.write_save_file("{ this is not json")
        self.assert_error(OSError, "The save file 'tasks.json' is corrupted (not valid JSON)",
                          self.backend.load_tasks)

    def test_save_file_with_wrong_structure_raises_os_error(self):
        self.write_save_file(json.dumps([1, 2, 3]))
        self.assert_error(OSError, "The save file 'tasks.json' has an unexpected format",
                          self.backend.load_tasks)

    def test_save_file_with_invalid_task_raises_os_error(self):
        self.write_save_file(json.dumps({"next_id": 2, "tasks": [self.saved_task(title="")]}))
        self.assert_error(OSError,
                          "The save file 'tasks.json' contains an invalid task: Title is required",
                          self.backend.load_tasks)

    def test_save_file_task_without_category_raises_os_error(self):
        record = self.saved_task()
        del record["category"]
        self.write_save_file(json.dumps({"next_id": 2, "tasks": [record]}))
        self.assert_error(OSError,
                          "The save file 'tasks.json' contains an invalid task: Category is required",
                          self.backend.load_tasks)

    def test_save_file_task_with_date_but_no_time_raises_os_error(self):
        record = self.saved_task(due_date="2026-10-05")
        self.write_save_file(json.dumps({"next_id": 2, "tasks": [record]}))
        self.assert_error(OSError,
                          "The save file 'tasks.json' contains an invalid task: " + DUE_DATE_ERROR,
                          self.backend.load_tasks)

    def test_save_file_with_duplicate_ids_raises_os_error(self):
        task = self.saved_task()
        self.write_save_file(json.dumps({"next_id": 2, "tasks": [task, task]}))
        self.assert_error(OSError, "The save file 'tasks.json' contains duplicate task ids",
                          self.backend.load_tasks)

    def test_failed_load_keeps_current_tasks(self):
        self.add(title="A")
        self.write_save_file("not json")
        with self.assertRaises(OSError):
            self.backend.load_tasks()
        self.assertEqual(self.ids(self.backend.get_all_tasks()), [1])

    def test_configure_with_invalid_path_is_rejected(self):
        self.assert_error(ValueError, "Data file must be a file path",
                          self.backend.configure, "   ")
