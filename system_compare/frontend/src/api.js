// All HTTP calls of the comparison app live here.
//
// This app has NO backend of its own. It talks to the two existing servers:
// the OOP System's server and the Imperative System's server. createClient()
// builds one set of functions per server, so every call goes to exactly one
// server and each system's answers stay separate.

// ----- The two systems ---------------------------------------------------------

export const SYSTEMS = [
  { id: "oop", name: "OOP System", url: "http://127.0.0.1:5001" },
  { id: "imperative", name: "Imperative System", url: "http://127.0.0.1:5002" },
];

export function portOf(system) {
  return new URL(system.url).port;
}

// ----- Due date format ---------------------------------------------------------
// The backends store due dates as "YYYY-MM-DD HH:MM". The form's
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

// ----- One client per server -----------------------------------------------------

// Returns an object with one function per server route. Each function resolves
// to the JSON data the server sent back, or throws an Error with the backend's
// message (or a "cannot connect" message when that server is not running).
export function createClient(serverUrl) {
  const apiBase = `${serverUrl}/api`;
  const serverPort = new URL(serverUrl).port;

  async function request(method, path, { params = {}, body } = {}) {
    const url = new URL(apiBase + path);
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
      throw new Error(`Cannot connect to the server on port ${serverPort}. Is it running?`);
    }

    const data = await response.json().catch(() => null);
    if (!response.ok) {
      throw new Error(data?.error ?? `Request failed with status ${response.status}`);
    }
    return data;
  }

  return {
    getOptions: () => request("GET", "/options"),
    queryTasks: (query) => request("GET", "/tasks", { params: query }),
    addTask: (fields) => request("POST", "/tasks", { body: withBackendDueDate(fields) }),
    updateTask: (taskId, fields) =>
      request("PUT", `/tasks/${taskId}`, { body: withBackendDueDate(fields) }),
    completeTask: (taskId) => request("PATCH", `/tasks/${taskId}/complete`),
    deleteTask: (taskId) => request("DELETE", `/tasks/${taskId}`),
    saveTasks: () => request("POST", "/save"),
    loadTasks: () => request("POST", "/load"),
  };
}
