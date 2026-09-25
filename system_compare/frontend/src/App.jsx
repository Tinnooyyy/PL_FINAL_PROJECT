import { useState } from "react";
import { SYSTEMS } from "./api.js";
import useSystem from "./useSystem.js";
import MessageBanner from "./components/MessageBanner.jsx";
import ModeSwitch from "./components/ModeSwitch.jsx";
import SystemHalf from "./components/SystemHalf.jsx";
import TaskForm from "./components/TaskForm.jsx";
import TaskList from "./components/TaskList.jsx";
import Toolbar from "./components/Toolbar.jsx";

// The search/filter/sort settings. Blank values mean "don't apply this step";
// the backend decides what that means.
const EMPTY_QUERY = {
  keyword: "",
  status: "",
  priority: "",
  category: "",
  sort_by: "",
  descending: false,
};

export default function App() {
  const [compare, setCompare] = useState(false);
  const [activeId, setActiveId] = useState(SYSTEMS[0].id);
  // ONE query for the whole screen: in Compare mode both systems get the
  // same search, filter and sort.
  const [query, setQuery] = useState(EMPTY_QUERY);

  // One independent state per system. A system only loads data while it is
  // on screen.
  const oop = useSystem(SYSTEMS[0], query, compare || activeId === SYSTEMS[0].id);
  const imperative = useSystem(SYSTEMS[1], query, compare || activeId === SYSTEMS[1].id);
  const allSystems = [oop, imperative];

  const active = allSystems.find((state) => state.system.id === activeId);
  // The systems that shared actions are sent to.
  const visible = compare ? allSystems : [active];
  // Both servers return the same options; use whichever one answered.
  const options = compare ? (oop.options ?? imperative.options) : active.options;

  function switchMode() {
    allSystems.forEach((state) => state.setEditingTask(null));
    setCompare((current) => !current);
  }

  // ----- Shared actions: sent to every visible system at the same time ----------

  // Adds the task to each visible system. Returns true (so the form clears)
  // when at least one server accepted it.
  async function addToVisible(fields) {
    const accepted = await Promise.all(visible.map((state) => state.addTask(fields)));
    return accepted.some((wasAccepted) => wasAccepted);
  }

  function saveVisible() {
    visible.forEach((state) => state.saveTasks());
  }

  function loadVisible() {
    visible.forEach((state) => state.loadTasks());
  }

  // Normal mode: the side form adds, or edits the active system's task.
  function submitNormalForm(fields) {
    return active.editingTask
      ? active.updateTask(active.editingTask, fields)
      : active.addTask(fields);
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header__inner">
          <div>
            <h1>Task &amp; To-Do Manager</h1>
            <p className="app-header__subtitle">
              Comparison app · uses both systems&apos; servers
            </p>
          </div>
          <ModeSwitch
            systems={SYSTEMS}
            activeId={activeId}
            compare={compare}
            onSelect={setActiveId}
            onToggleCompare={switchMode}
          />
        </div>
      </header>

      {compare ? (
        <main className="compare-layout">
          <section className="panel shared-form" aria-label="Shared task form">
            <p className="shared-form__note">
              New tasks are sent to <strong>both</strong> servers. To edit, complete
              or delete, use the buttons on a task inside each half.
            </p>
            <TaskForm
              key={options ? "ready" : "waiting"}
              task={null}
              options={options}
              onSubmit={addToVisible}
              onCancel={() => {}}
            />
          </section>

          <Toolbar
            query={query}
            options={options}
            onChange={setQuery}
            onReset={() => setQuery(EMPTY_QUERY)}
            onSave={saveVisible}
            onLoad={loadVisible}
          />

          <div className="halves">
            {allSystems.map((state) => (
              <SystemHalf key={state.system.id} state={state} />
            ))}
          </div>
        </main>
      ) : (
        <main className="layout">
          <MessageBanner error={active.error} notice={active.notice}
            onRetry={active.refresh} onDismiss={active.dismiss} />

          <section className="panel layout__form" aria-label="Task form">
            <TaskForm
              key={`${activeId}-${active.editingTask?.id ?? "new"}-${options ? "ready" : "waiting"}`}
              task={active.editingTask}
              options={options}
              onSubmit={submitNormalForm}
              onCancel={() => active.setEditingTask(null)}
            />
          </section>

          <section className="layout__list" aria-label="Tasks">
            <Toolbar
              query={query}
              options={options}
              onChange={setQuery}
              onReset={() => setQuery(EMPTY_QUERY)}
              onSave={saveVisible}
              onLoad={loadVisible}
            />
            <TaskList
              tasks={active.tasks}
              editingId={active.editingTask?.id}
              onEdit={active.setEditingTask}
              onComplete={active.completeTask}
              onDelete={active.deleteTask}
            />
          </section>
        </main>
      )}
    </div>
  );
}
