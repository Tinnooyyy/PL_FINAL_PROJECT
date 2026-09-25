import { portOf } from "../api.js";

// Header controls: pick one system (normal mode) or turn on Compare mode.
// Also says which system is active and on which port its server runs.
export default function ModeSwitch({ systems, activeId, compare, onSelect, onToggleCompare }) {
  const active = systems.find((system) => system.id === activeId);

  return (
    <div className="mode">
      <div className="mode__controls">
        <div className="segmented" role="group" aria-label="Choose system">
          {systems.map((system) => (
            <button
              key={system.id}
              type="button"
              className="segmented__option"
              aria-pressed={!compare && system.id === activeId}
              disabled={compare}
              onClick={() => onSelect(system.id)}
            >
              {system.name}
            </button>
          ))}
        </div>
        <button type="button" className="compare-toggle" aria-pressed={compare}
          onClick={onToggleCompare}>
          <span className="compare-toggle__track" aria-hidden="true">
            <span className="compare-toggle__thumb" />
          </span>
          Compare
        </button>
      </div>

      <p className="mode__status">
        {compare ? (
          <>
            Comparing {systems.map((system, index) => (
              <span key={system.id}>
                {index > 0 && " and "}
                <strong>{system.name}</strong> (port <code>{portOf(system)}</code>)
              </span>
            ))}
          </>
        ) : (
          <>
            Active: <strong>{active.name}</strong> · server port <code>{portOf(active)}</code>
          </>
        )}
      </p>
    </div>
  );
}
