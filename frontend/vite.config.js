import { defineConfig } from "vite";

// Vite compiles the .jsx files itself, so no extra React plugin is needed.
export default defineConfig({
  server: {
    port: 5173,
  },
});
