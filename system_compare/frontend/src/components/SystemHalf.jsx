import { portOf } from "../api.js";
import MessageBanner from "./MessageBanner.jsx";
import TaskForm from "./TaskForm.jsx";
import TaskList from "./TaskList.jsx";

// One half of the Compare screen: one system's label, messages and task list.
//
// Complete / Edit / Delete here only talk to THIS system's server, because the
// same task can have a different id in the other system. Editing opens the
// normal task form inside this half.
export default function SystemHalf({ state }) {
  const { system, options, tasks, error, notice, editingTask } = state;

  return (
    <section className="half" aria-label={system.name}>
      <header className="half__header">
        <span className="system__name">{system.name}</span>
        <span className="system__server">
          Server port <code>{portOf(system)}</code>
        </span>
      </header>

      <MessageBanner error={error} notice={notice} onRetry={state.refresh}
        onDismiss={state.dismiss} />

      {editingTask && (
        <div className="panel half__edit">
          <TaskForm
            key={editingTask.id}
            task={editingTask}
            options={options}
            onSubmit={(fields) => state.updateTask(editingTask, fields)}
            onCancel={() => state.setEditingTask(null)}
          />
        </div>
      )}

      <TaskList
        tasks={tasks}
        editingId={editingTask?.id}
        onEdit={state.setEditingTask}
        onComplete={state.completeTask}
        onDelete={state.deleteTask}
      />
    </section>
  );
}
