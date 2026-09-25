// Shows the backend's error message (red) or a success notice (green).
// Errors get a "Retry" button, which reloads the data from the server; this
// helps when the server was started after the page was opened.
export default function MessageBanner({ error, notice, onRetry, onDismiss }) {
  if (!error && !notice) return null;

  return (
    <div className={`banner ${error ? "banner--error" : "banner--notice"}`}
      role={error ? "alert" : "status"}>
      <p>
        {error ? (
          <>
            <strong>Error:</strong> {error}
          </>
        ) : (
          notice
        )}
      </p>
      <div className="banner__actions">
        {error && (
          <button type="button" className="button button--small" onClick={onRetry}>
            Retry
          </button>
        )}
        <button type="button" className="banner__close" onClick={onDismiss}
          aria-label="Dismiss message">
          ×
        </button>
      </div>
    </div>
  );
}
