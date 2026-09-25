import { formatLabel } from "../labels.js";

// Search, filter and sort controls, plus the Save / Load buttons.
// Changing a control only updates the query; App sends it to the backend.
export default function Toolbar({ query, options, onChange, onReset, onSave, onLoad }) {
  function update(name, value) {
    onChange({ ...query, [name]: value });
  }

  return (
    <div className="panel toolbar">
      <label className="field toolbar__search">
        <span>Search</span>
        <input type="search" value={query.keyword}
          onChange={(e) => update("keyword", e.target.value)}
          placeholder="Keyword in title or description" />
      </label>

      <label className="field">
        <span>Status</span>
        <select value={query.status} onChange={(e) => update("status", e.target.value)}>
          <option value="">All</option>
          {(options?.statuses ?? []).map((value) => (
            <option key={value} value={value}>{formatLabel(value)}</option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Priority</span>
        <select value={query.priority} onChange={(e) => update("priority", e.target.value)}>
          <option value="">All</option>
          {(options?.priorities ?? []).map((value) => (
            <option key={value} value={value}>{formatLabel(value)}</option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Category</span>
        <select value={query.category} onChange={(e) => update("category", e.target.value)}>
          <option value="">All</option>
          {(options?.categories ?? []).map((value) => (
            <option key={value} value={value}>{formatLabel(value)}</option>
          ))}
        </select>
      </label>

      <label className="field">
        <span>Sort by</span>
        <select value={query.sort_by} onChange={(e) => update("sort_by", e.target.value)}>
          <option value="">Order added</option>
          {(options?.sort_fields ?? []).map((value) => (
            <option key={value} value={value}>{formatLabel(value)}</option>
          ))}
        </select>
      </label>

      <label className="checkbox">
        <input type="checkbox" checked={query.descending}
          onChange={(e) => update("descending", e.target.checked)} />
        Descending
      </label>

      <div className="toolbar__buttons">
        <button type="button" className="button" onClick={onReset}>Clear</button>
        <button type="button" className="button" onClick={onSave}>Save</button>
        <button type="button" className="button" onClick={onLoad}>Load</button>
      </div>
    </div>
  );
}
