import { formatLabel } from "../labels.js";

// One task card. The buttons just report the click; App calls the backend.
export default function TaskItem({ task, isEditing, onEdit, onComplete, onDelete }) {
  return (
    <li className={`panel task${isEditing ? " task--editing" : ""}`}
      data-status={task.status}>
      <div className="task__main">
        <h3 className="task__title">
          <span className="task__id">#{task.id}</span> {task.title}
        </h3>
        {task.description && <p className="task__description">{task.description}</p>}
        <div className="task__meta">
          <span className="tag" data-priority={task.priority}>
            {formatLabel(task.priority)} priority
          </span>
          <span className="tag" data-status={task.status}>{formatLabel(task.status)}</span>
          <span className="tag" data-category={task.category}>{formatLabel(task.category)}</span>
          <span className="task__due">
            {task.due_date ? `Due ${task.due_date}` : "No due date"}
          </span>
        </div>
      </div>
      <div className="task__actions">
        <button type="button" className="button button--small" onClick={() => onComplete(task)}>
          Complete
        </button>
        <button type="button" className="button button--small" onClick={() => onEdit(task)}>
          Edit
        </button>
        <button type="button" className="button button--small button--danger"
          onClick={() => onDelete(task)}>
          Delete
        </button>
      </div>
    </li>
  );
}
