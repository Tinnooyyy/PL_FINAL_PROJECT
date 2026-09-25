import { defineConfig } from "vite";

// Vite compiles the .jsx files itself, so no extra React plugin is needed.
export default defineConfig({
  server: {
    port: 5175,
    // Fail instead of silently picking another port: both servers only accept
    // requests from this exact port.
    strictPort: true,
  },
});
