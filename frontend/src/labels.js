// Display helpers only: they change how values look, never what they mean.

export const BACKEND_LABELS = {
  oop: "Object-Oriented",
  imperative: "Imperative",
};

// "in_progress" -> "In progress", "due_date" -> "Due date"
export function formatLabel(value) {
  const text = String(value).replaceAll("_", " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}
