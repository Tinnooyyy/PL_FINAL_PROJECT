import { BACKEND_LABELS } from "../labels.js";

// Shows the backend's error message (red) or a success notice (green).
export default function MessageBanner({ error, notice, backend, onDismiss }) {
  if (!error && !notice) return null;

  return (
    <div className={`banner ${error ? "banner--error" : "banner--notice"}`}
      role={error ? "alert" : "status"}>
      <p>
        {error ? (
          <>
            <strong>{BACKEND_LABELS[backend]} backend error:</strong> {error}
          </>
        ) : (
          notice
        )}
      </p>
      <button type="button" className="banner__close" onClick={onDismiss}
        aria-label="Dismiss message">
        ×
      </button>
    </div>
  );
}
