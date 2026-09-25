// Display helper only: it changes how values look, never what they mean.

// "in_progress" -> "In progress", "due_date" -> "Due date"
export function formatLabel(value) {
  const text = String(value).replaceAll("_", " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}
