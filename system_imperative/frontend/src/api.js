// All HTTP calls to this system's server live here.
//
// Each function resolves to the JSON data the server sent back. On failure it
// throws an Error whose message is the backend's error text, or a
// "cannot connect" message when the server is not running.

// ----- System settings ---------------------------------------------------------
// These two values are the only difference between the OOP and the Imperative
// front ends (apart from the port in vite.config.js).
export const SYSTEM_NAME = "Imperative System";
export const SERVER_URL = "http://127.0.0.1:5002";

const API_BASE = `${SERVER_URL}/api`;
const SERVER_PORT = new URL(SERVER_URL).port;

async function request(method, path, { params = {}, body } = {}) {
  const url = new URL(API_BASE + path);
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
    throw new Error(`Cannot connect to the server on port ${SERVER_PORT}. Is it running?`);
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    throw new Error(data?.error ?? `Request failed with status ${response.status}`);
  }
  return data;
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

// ----- One function per server route ---------------------------------------------

export function getOptions() {
  return request("GET", "/options");
}

export function queryTasks(query) {
  return request("GET", "/tasks", { params: query });
}

export function addTask(fields) {
  return request("POST", "/tasks", { body: withBackendDueDate(fields) });
}

export function updateTask(taskId, fields) {
  return request("PUT", `/tasks/${taskId}`, { body: withBackendDueDate(fields) });
}

export function completeTask(taskId) {
  return request("PATCH", `/tasks/${taskId}/complete`);
}

export function deleteTask(taskId) {
  return request("DELETE", `/tasks/${taskId}`);
}

export function saveTasks() {
  return request("POST", "/save");
}

export function loadTasks() {
  return request("POST", "/load");
}
