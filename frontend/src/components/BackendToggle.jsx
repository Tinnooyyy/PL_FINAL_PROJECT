import { BACKEND_LABELS } from "../labels.js";

// The OOP / Imperative switch, plus a label showing which backend is active
// and which one actually answered the last request (from the X-Backend header).
export default function BackendToggle({ backend, servedBy, onChange }) {
  return (
    <div className="backend">
      <div className="backend__switch" role="group" aria-label="Choose backend">
        {Object.entries(BACKEND_LABELS).map(([name, label]) => (
          <button
            key={name}
            type="button"
            className="backend__option"
            data-name={name}
            aria-pressed={backend === name}
            onClick={() => onChange(name)}
          >
            {label}
          </button>
        ))}
      </div>
      <p className="backend__status">
        <span className="backend__dot" aria-hidden="true" />
        Active backend: <strong>{BACKEND_LABELS[backend]} Python</strong>
        {servedBy && (
          <span className="backend__served"> · last response from <code>{servedBy}</code></span>
        )}
      </p>
    </div>
  );
}
