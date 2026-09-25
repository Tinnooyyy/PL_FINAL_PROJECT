import { useCallback, useEffect, useMemo, useState } from "react";
import { createClient } from "./api.js";

// Everything the screen needs for ONE system: its options, its task list,
// its own error / notice message and the task being edited, plus one function
// per action that calls that system's server.
//
// The app uses this hook once for each system, so the two systems never share
// state: an error from one server only ever shows up in that system's area.
//
// `active` is false when the system is not on screen; it then stops loading.
export default function useSystem(system, query, active) {
  const client = useMemo(() => createClient(system.url), [system.url]);

  const [options, setOptions] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [editingTask, setEditingTask] = useState(null);
  // Bumped after every change so the task list is fetched again.
  const [refreshCount, setRefreshCount] = useState(0);

  // Every server call goes through here. Returns the data, or undefined on error.
  const run = useCallback(async (apiCall) => {
    try {
      const data = await apiCall();
      setError("");
      return data;
    } catch (err) {
      setError(err.message);
      setNotice("");
      return undefined;
    }
  }, []);

  const refresh = useCallback(() => setRefreshCount((count) => count + 1), []);

  // Load the allowed values (again after every refresh, so "Retry" works).
  useEffect(() => {
    if (!active) return undefined;
    let ignore = false;
    run(() => client.getOptions()).then((data) => {
      if (!ignore && data !== undefined) setOptions(data);
    });
    return () => {
      ignore = true;
    };
  }, [active, client, refreshCount, run]);

  // Load the task list whenever the query or the data changes.
  useEffect(() => {
    if (!active) return undefined;
    let ignore = false; // skip answers to requests that are already out of date
    run(() => client.queryTasks(query)).then((data) => {
      if (!ignore && data !== undefined) setTasks(data);
    });
    return () => {
      ignore = true;
    };
  }, [active, client, query, refreshCount, run]);

  // ----- Actions (each returns true when the server accepted it) -----------------

  async function addTask(fields) {
    const data = await run(() => client.addTask(fields));
    if (data === undefined) return false;
    setNotice(`Task #${data.id} added.`);
    refresh();
    return true;
  }

  async function updateTask(task, fields) {
    const data = await run(() => client.updateTask(task.id, fields));
    if (data === undefined) return false;
    setNotice(`Task #${data.id} updated.`);
    setEditingTask(null);
    refresh();
    return true;
  }

  async function completeTask(task) {
    const data = await run(() => client.completeTask(task.id));
    if (data === undefined) return false;
    setNotice(`Task #${data.id} marked as completed.`);
    refresh();
    return true;
  }

  async function deleteTask(task) {
    if (!window.confirm(`Delete "${task.title}" from the ${system.name}?`)) return false;
    const data = await run(() => client.deleteTask(task.id));
    if (data === undefined) return false;
    if (editingTask?.id === data.id) setEditingTask(null);
    setNotice(`Task #${data.id} deleted.`);
    refresh();
    return true;
  }

  async function saveTasks() {
    const data = await run(() => client.saveTasks());
    if (data === undefined) return false;
    setNotice(`Saved ${data.saved} task(s) to the save file.`);
    return true;
  }

  async function loadTasks() {
    const data = await run(() => client.loadTasks());
    if (data === undefined) return false;
    setEditingTask(null);
    setNotice(`Loaded ${data.loaded} task(s) from the save file.`);
    refresh();
    return true;
  }

  function dismiss() {
    setError("");
    setNotice("");
  }

  return {
    system,
    options,
    tasks,
    error,
    notice,
    editingTask,
    setEditingTask,
    refresh,
    dismiss,
    addTask,
    updateTask,
    completeTask,
    deleteTask,
    saveTasks,
    loadTasks,
  };
}
