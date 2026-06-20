import { useMemo, useState } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const PRIORITY_SCORE = {
  low: 25,
  medium: 50,
  high: 75,
  critical: 100,
};

export default function WhatIfPanel({ prediction }) {
  const [form, setForm] = useState({
    expected_crowd_size: 25000,
    event_duration_hours: 6,
    impact_score: 85,
    closure_probability: 0.82,
    priority: "critical",
    peak_hour: true,
    nearby_sensitive_zone: true,
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const update = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const originalScenario = useMemo(
    () => ({
      impact_score: prediction?.impact_score ?? 0,
      closure_probability: prediction?.closure_probability ?? 0,
      priority: prediction?.priority ?? "medium",
      expected_crowd_size: 18000,
      event_duration_hours: prediction?.expected_duration_hours_p50 ?? 0,
      peak_hour: true,
      nearby_sensitive_zone: true,
    }),
    [prediction]
  );

  const modifiedScenario = useMemo(
    () => ({
      expected_crowd_size: Number(form.expected_crowd_size) || 0,
      event_duration_hours: Number(form.event_duration_hours) || 0,
      impact_score: Number(form.impact_score) || 0,
      closure_probability: Number(form.closure_probability) || 0,
      priority: form.priority,
      peak_hour: Boolean(form.peak_hour),
      nearby_sensitive_zone: Boolean(form.nearby_sensitive_zone),
    }),
    [form]
  );

  const runWhatIf = async () => {
    if (!prediction) {
      alert("Run Demo Scenario or Video Intelligence first.");
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API}/what-if`, {
        original_scenario: originalScenario,
        modifications: modifiedScenario,
      });

      setResult(response.data);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card whatif-card">
      <div className="section-header">
        <div>
          <h2>What-If Simulator</h2>
          <p>
            Adjust traffic conditions and compare the changed scenario with the
            active forecast through visual bars.
          </p>
        </div>
      </div>

      <div className="whatif-form">
        <Input
          label="Expected Crowd Size"
          type="number"
          value={form.expected_crowd_size}
          onChange={(v) => update("expected_crowd_size", v)}
        />

        <Input
          label="Event Duration Hours"
          type="number"
          value={form.event_duration_hours}
          onChange={(v) => update("event_duration_hours", v)}
        />

        <Input
          label="Impact Score"
          type="number"
          value={form.impact_score}
          onChange={(v) => update("impact_score", v)}
        />

        <Input
          label="Closure Probability"
          type="number"
          step="0.01"
          value={form.closure_probability}
          onChange={(v) => update("closure_probability", v)}
        />

        <label className="field">
          <span>Priority</span>
          <select
            value={form.priority}
            onChange={(e) => update("priority", e.target.value)}
          >
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="critical">Critical</option>
          </select>
        </label>

        <label className="field">
          <span>Peak Hour</span>
          <select
            value={String(form.peak_hour)}
            onChange={(e) => update("peak_hour", e.target.value === "true")}
          >
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </label>

        <label className="field full-field">
          <span>Nearby Sensitive Zone</span>
          <select
            value={String(form.nearby_sensitive_zone)}
            onChange={(e) =>
              update("nearby_sensitive_zone", e.target.value === "true")
            }
          >
            <option value="true">Yes</option>
            <option value="false">No</option>
          </select>
        </label>
      </div>

      <button className="primary-btn" onClick={runWhatIf} disabled={loading}>
        {loading ? "Running..." : "Run What-If"}
      </button>

      {result && (
        <div className="whatif-result">
          <h3>Operational Impact Graphs</h3>

          <ScenarioCharts original={originalScenario} modified={modifiedScenario} />

          <RiskShiftChart
            original={result.comparison.risk_level_change.from}
            modified={result.comparison.risk_level_change.to}
          />

          <GroupedBars
            title="Resource Deployment Change"
            rows={[
              {
                label: "Manpower",
                original: result.original_plan.manpower,
                modified: result.modified_plan.manpower,
                max: Math.max(result.original_plan.manpower, result.modified_plan.manpower, 1),
              },
              {
                label: "Barricades",
                original: result.original_plan.barricades,
                modified: result.modified_plan.barricades,
                max: Math.max(result.original_plan.barricades, result.modified_plan.barricades, 1),
              },
              {
                label: "Patrol Units",
                original: result.original_plan.patrol_units,
                modified: result.modified_plan.patrol_units,
                max: Math.max(result.original_plan.patrol_units, result.modified_plan.patrol_units, 1),
              },
              {
                label: "Emergency Units",
                original: result.original_plan.emergency_units,
                modified: result.modified_plan.emergency_units,
                max: Math.max(result.original_plan.emergency_units, result.modified_plan.emergency_units, 1),
              },
            ]}
          />
        </div>
      )}
    </div>
  );
}

function ScenarioCharts({ original, modified }) {
  const rows = [
    {
      label: "Crowd Size",
      original: original.expected_crowd_size,
      modified: modified.expected_crowd_size,
      max: Math.max(original.expected_crowd_size, modified.expected_crowd_size, 1),
      format: compactNumber,
    },
    {
      label: "Duration",
      original: original.event_duration_hours,
      modified: modified.event_duration_hours,
      max: Math.max(original.event_duration_hours, modified.event_duration_hours, 1),
      suffix: "h",
    },
    {
      label: "Impact Score",
      original: original.impact_score,
      modified: modified.impact_score,
      max: 100,
    },
    {
      label: "Closure Risk",
      original: Math.round(original.closure_probability * 100),
      modified: Math.round(modified.closure_probability * 100),
      max: 100,
      suffix: "%",
    },
    {
      label: "Priority",
      original: PRIORITY_SCORE[original.priority] ?? 50,
      modified: PRIORITY_SCORE[modified.priority] ?? 50,
      max: 100,
      originalDisplay: capitalize(original.priority),
      modifiedDisplay: capitalize(modified.priority),
    },
    {
      label: "Peak Hour",
      original: original.peak_hour ? 100 : 0,
      modified: modified.peak_hour ? 100 : 0,
      max: 100,
      originalDisplay: original.peak_hour ? "Yes" : "No",
      modifiedDisplay: modified.peak_hour ? "Yes" : "No",
    },
    {
      label: "Sensitive Zone",
      original: original.nearby_sensitive_zone ? 100 : 0,
      modified: modified.nearby_sensitive_zone ? 100 : 0,
      max: 100,
      originalDisplay: original.nearby_sensitive_zone ? "Yes" : "No",
      modifiedDisplay: modified.nearby_sensitive_zone ? "Yes" : "No",
    },
  ];

  return (
    <div className="parameter-chart-section">
      <div className="chart-title-row">
        <h3>Manual Parameter Graphs</h3>
        <div className="chart-legend">
          <span className="legend-original">Original</span>
          <span className="legend-modified">Modified</span>
        </div>
      </div>

      <div className="parameter-chart-grid">
        {rows.map((row) => (
          <ParameterChart key={row.label} row={row} />
        ))}
      </div>
    </div>
  );
}

function ParameterChart({ row }) {
  const originalWidth = getWidth(row.original, row.max);
  const modifiedWidth = getWidth(row.modified, row.max);
  const originalValue = row.originalDisplay ?? formatValue(row.original, row);
  const modifiedValue = row.modifiedDisplay ?? formatValue(row.modified, row);

  return (
    <div className="parameter-chart-card">
      <div className="parameter-chart-head">
        <strong>{row.label}</strong>
      </div>

      <BarLine label="Original" value={originalValue} width={originalWidth} type="original" />
      <BarLine label="Modified" value={modifiedValue} width={modifiedWidth} type="modified" />
    </div>
  );
}

function RiskShiftChart({ original, modified }) {
  const riskScore = {
    low: 25,
    medium: 50,
    high: 75,
    critical: 100,
  };

  return (
    <div className="parameter-chart-card wide-chart-card">
      <div className="parameter-chart-head">
        <strong>Risk Level Shift</strong>
      </div>

      <BarLine
        label="Original"
        value={capitalize(original)}
        width={riskScore[String(original).toLowerCase()] ?? 50}
        type="original"
      />
      <BarLine
        label="Modified"
        value={capitalize(modified)}
        width={riskScore[String(modified).toLowerCase()] ?? 50}
        type="modified"
      />
    </div>
  );
}

function GroupedBars({ title, rows }) {
  return (
    <div className="group-chart">
      <div className="chart-title-row">
        <h3>{title}</h3>
        <div className="chart-legend">
          <span className="legend-original">Original</span>
          <span className="legend-modified">Modified</span>
        </div>
      </div>

      <div className="resource-chart-grid">
        {rows.map((row) => (
          <div className="parameter-chart-card" key={row.label}>
            <div className="parameter-chart-head">
              <strong>{row.label}</strong>
            </div>

            <BarLine
              label="Original"
              value={row.original}
              width={getWidth(row.original, row.max)}
              type="original"
            />
            <BarLine
              label="Modified"
              value={row.modified}
              width={getWidth(row.modified, row.max)}
              type="modified"
            />
          </div>
        ))}
      </div>
    </div>
  );
}

function BarLine({ label, value, width, type }) {
  return (
    <div className="bar-line">
      <span>{label}</span>
      <div className="bar-track">
        <div className={`bar-fill ${type}-bar`} style={{ width: `${width}%` }} />
      </div>
      <strong>{value}</strong>
    </div>
  );
}

function Input({ label, value, onChange, type = "text", step }) {
  return (
    <label className="field">
      <span>{label}</span>
      <input
        type={type}
        step={step}
        value={value}
        onChange={(e) => onChange(e.target.value)}
      />
    </label>
  );
}

function getWidth(value, max) {
  if (!Number.isFinite(Number(value)) || !Number.isFinite(Number(max)) || Number(max) <= 0) {
    return 0;
  }

  return Math.max(4, Math.min((Number(value) / Number(max)) * 100, 100));
}

function formatValue(value, row) {
  const formatter = row.format ?? ((v) => v);
  return `${formatter(value)}${row.suffix || ""}`;
}

function compactNumber(value) {
  return new Intl.NumberFormat("en-IN", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(Number(value) || 0);
}

function capitalize(value) {
  if (!value) return "—";
  return String(value).charAt(0).toUpperCase() + String(value).slice(1);
}
