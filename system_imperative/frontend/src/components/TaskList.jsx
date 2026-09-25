import TaskItem from "./TaskItem.jsx";

// Shows the tasks exactly in the order the backend returned them.
export default function TaskList({ tasks, editingId, onEdit, onComplete, onDelete }) {
  return (
    <div className="task-list">
      <p className="task-list__count">{tasks.length} task(s)</p>
      {tasks.length === 0 ? (
        <p className="panel task-list__empty">No tasks to show.</p>
      ) : (
        <ul>
          {tasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              isEditing={task.id === editingId}
              onEdit={onEdit}
              onComplete={onComplete}
              onDelete={onDelete}
            />
          ))}
        </ul>
      )}
    </div>
  );
}
