// All HTTP calls to the Flask API live here. Every call sends the chosen
// backend as ?backend=oop or ?backend=imperative.
//
// Each function resolves to { data, servedBy }, where servedBy is the backend
// name the API reports in its X-Backend header. On failure it throws an Error
// whose message is the backend's error text.

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:5000/api";

async function request(backend, method, path, { params = {}, body } = {}) {
  const url = new URL(API_BASE + path);
  url.searchParams.set("backend", backend);
  for (const [name, value] of Object.entries(params)) {
    url.searchParams.set(name, value);
  }

  let response;
  try {
    response = await fetch(url, {
      method,
      headers: body === undefined ? {} : { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error(
      `Cannot reach the API at ${API_BASE}. Is it running? (python api/app.py)`,
    );
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.error ?? `Request failed with status ${response.status}`);
  }
  return { data, servedBy: response.headers.get("X-Backend") };
}

export function getOptions(backend) {
  return request(backend, "GET", "/options");
}

export function queryTasks(backend, query) {
  return request(backend, "GET", "/tasks", { params: query });
}

// ----- Due date format ---------------------------------------------------------
// The backend stores due dates as "YYYY-MM-DD HH:MM". The form's
// <input type="datetime-local"> uses "YYYY-MM-DDTHH:MM". These helpers are the
// only place where one is turned into the other. An empty value stays empty.

export function dueDateToInput(dueDate) {
  return dueDate.replace(" ", "T");
}

function dueDateFromInput(value) {
  return value.replace("T", " ");
}

function withBackendDueDate(fields) {
  return { ...fields, due_date: dueDateFromInput(fields.due_date) };
}

export function addTask(backend, fields) {
  return request(backend, "POST", "/tasks", { body: withBackendDueDate(fields) });
}

export function updateTask(backend, taskId, fields) {
  return request(backend, "PUT", `/tasks/${taskId}`, { body: withBackendDueDate(fields) });
}

export function completeTask(backend, taskId) {
  return request(backend, "PATCH", `/tasks/${taskId}/complete`);
}

export function deleteTask(backend, taskId) {
  return request(backend, "DELETE", `/tasks/${taskId}`);
}

export function saveTasks(backend) {
  return request(backend, "POST", "/save");
}

export function loadTasks(backend) {
  return request(backend, "POST", "/load");
}
