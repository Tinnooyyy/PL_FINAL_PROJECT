import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { SYSTEM_NAME } from "./api.js";
import App from "./App.jsx";
import "./styles.css";

// Show the system name in the browser tab, e.g. "OOP System · Task Manager".
document.title = `${SYSTEM_NAME} · Task Manager`;

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
