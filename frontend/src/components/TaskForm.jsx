import { useState } from "react";
import { formatLabel } from "../labels.js";

// Starting values: the task being edited, or blanks plus the backend's defaults.
function initialFields(task, options) {
  if (task) {
    return {
      title: task.title,
      description: task.description,
      due_date: task.due_date,
      priority: task.priority,
      status: task.status,
    };
  }
  return {
    title: "",
    description: "",
    due_date: "",
    priority: options?.defaults.priority ?? "",
    status: options?.defaults.status ?? "",
  };
}

// Add / edit form. It does no validation: whatever is typed is sent to the
// backend, and any problem comes back as an error message.
export default function TaskForm({ task, options, onSubmit, onCancel }) {
  const [fields, setFields] = useState(() => initialFields(task, options));
  const [busy, setBusy] = useState(false);

  function update(name, value) {
    setFields((current) => ({ ...current, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setBusy(true);
    const accepted = await onSubmit(fields);
    setBusy(false);
    if (accepted && !task) setFields(initialFields(null, options));
  }

  return (
    <form className="form" onSubmit={handleSubmit} noValidate>
      <h2>{task ? `Edit task #${task.id}` : "Add a task"}</h2>

      <label className="field">
        <span>Title</span>
        <input value={fields.title} onChange={(e) => update("title", e.target.value)}
          placeholder="e.g. Submit project report" />
      </label>

      <label className="field">
        <span>Description</span>
        <textarea rows={3} value={fields.description}
          onChange={(e) => update("description", e.target.value)}
          placeholder="Optional details" />
      </label>

      <label className="field">
        <span>Due date</span>
        <input value={fields.due_date} onChange={(e) => update("due_date", e.target.value)}
          placeholder="YYYY-MM-DD" inputMode="numeric" />
        <small>Leave empty for no due date.</small>
      </label>

      <div className="field-row">
        <label className="field">
          <span>Priority</span>
          <select value={fields.priority} onChange={(e) => update("priority", e.target.value)}>
            {(options?.priorities ?? []).map((value) => (
              <option key={value} value={value}>{formatLabel(value)}</option>
            ))}
          </select>
        </label>

        <label className="field">
          <span>Status</span>
          <select value={fields.status} onChange={(e) => update("status", e.target.value)}>
            {(options?.statuses ?? []).map((value) => (
              <option key={value} value={value}>{formatLabel(value)}</option>
            ))}
          </select>
        </label>
      </div>

      <div className="form__actions">
        <button type="submit" className="button button--primary" disabled={busy}>
          {task ? "Save changes" : "Add task"}
        </button>
        {task && (
          <button type="button" className="button" onClick={onCancel}>Cancel</button>
        )}
      </div>
    </form>
  );
}
