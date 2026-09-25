import { useCallback, useEffect, useState } from "react";
import * as api from "./api.js";
import { BACKEND_LABELS } from "./labels.js";
import BackendToggle from "./components/BackendToggle.jsx";
import MessageBanner from "./components/MessageBanner.jsx";
import TaskForm from "./components/TaskForm.jsx";
import TaskList from "./components/TaskList.jsx";
import Toolbar from "./components/Toolbar.jsx";

// The search/filter/sort settings. Blank values mean "don't apply this step";
// the backend decides what that means.
const EMPTY_QUERY = {
  keyword: "",
  status: "",
  priority: "",
  sort_by: "",
  descending: false,
};

export default function App() {
  const [backend, setBackend] = useState("oop");
  const [options, setOptions] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [query, setQuery] = useState(EMPTY_QUERY);
  const [editingTask, setEditingTask] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [servedBy, setServedBy] = useState("");
  // Bumped after every change so the task list is fetched again.
  const [refreshCount, setRefreshCount] = useState(0);

  // Every API call goes through here, so errors and the "served by" label
  // are handled the same way everywhere. Returns the data, or undefined on error.
  const run = useCallback(async (apiCall) => {
    try {
      const result = await apiCall();
      setServedBy(result.servedBy);
      setError("");
      return result.data;
    } catch (err) {
      setError(err.message);
      setNotice("");
      return undefined;
    }
  }, []);

  // Load the allowed values whenever the backend changes.
  useEffect(() => {
    let ignore = false;
    run(() => api.getOptions(backend)).then((data) => {
      if (!ignore && data !== undefined) setOptions(data);
    });
    return () => {
      ignore = true;
    };
  }, [backend, run]);

  // Load the task list whenever the backend, the query or the data changes.
  useEffect(() => {
    let ignore = false; // skip answers to requests that are already out of date
    run(() => api.queryTasks(backend, query)).then((data) => {
      if (!ignore && data !== undefined) setTasks(data);
    });
    return () => {
      ignore = true;
    };
  }, [backend, query, refreshCount, run]);

  function refresh() {
    setRefreshCount((count) => count + 1);
  }

  function switchBackend(name) {
    setBackend(name);
    setEditingTask(null);
    setError("");
    setNotice("");
  }

  // Returns true when the backend accepted the task, so the form can clear itself.
  async function handleSubmit(fields) {
    const data = editingTask
      ? await run(() => api.updateTask(backend, editingTask.id, fields))
      : await run(() => api.addTask(backend, fields));
    if (data === undefined) return false;

    setNotice(editingTask ? `Task #${data.id} updated.` : `Task #${data.id} added.`);
    setEditingTask(null);
    refresh();
    return true;
  }

  async function handleComplete(task) {
    const data = await run(() => api.completeTask(backend, task.id));
    if (data === undefined) return;
    setNotice(`Task #${data.id} marked as completed.`);
    refresh();
  }

  async function handleDelete(task) {
    if (!window.confirm(`Delete "${task.title}"?`)) return;
    const data = await run(() => api.deleteTask(backend, task.id));
    if (data === undefined) return;
    if (editingTask?.id === data.id) setEditingTask(null);
    setNotice(`Task #${data.id} deleted.`);
    refresh();
  }

  async function handleSave() {
    const data = await run(() => api.saveTasks(backend));
    if (data === undefined) return;
    setNotice(`Saved ${data.saved} task(s) to the ${BACKEND_LABELS[backend]} save file.`);
  }

  async function handleLoad() {
    const data = await run(() => api.loadTasks(backend));
    if (data === undefined) return;
    setEditingTask(null);
    setNotice(`Loaded ${data.loaded} task(s) from the ${BACKEND_LABELS[backend]} save file.`);
    refresh();
  }

  return (
    <div className="app" data-backend={backend}>
      <header className="app-header">
        <div className="app-header__inner">
          <div>
            <h1>Task &amp; To-Do Manager</h1>
            <p className="app-header__subtitle">
              One React front end, two interchangeable Python backends
            </p>
          </div>
          <BackendToggle backend={backend} servedBy={servedBy} onChange={switchBackend} />
        </div>
      </header>

      <main className="layout">
        <MessageBanner error={error} notice={notice} backend={backend}
          onDismiss={() => { setError(""); setNotice(""); }} />

        <section className="panel layout__form" aria-label="Task form">
          <TaskForm
            // A new key gives a fresh form when switching task, backend or options.
            key={`${backend}-${editingTask?.id ?? "new"}-${options ? "ready" : "waiting"}`}
            task={editingTask}
            options={options}
            onSubmit={handleSubmit}
            onCancel={() => setEditingTask(null)}
          />
        </section>

        <section className="layout__list" aria-label="Tasks">
          <Toolbar
            query={query}
            options={options}
            onChange={setQuery}
            onReset={() => setQuery(EMPTY_QUERY)}
            onSave={handleSave}
            onLoad={handleLoad}
          />
          <TaskList
            tasks={tasks}
            editingId={editingTask?.id}
            onEdit={setEditingTask}
            onComplete={handleComplete}
            onDelete={handleDelete}
          />
        </section>
      </main>
    </div>
  );
}
