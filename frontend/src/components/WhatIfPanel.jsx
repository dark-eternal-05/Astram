import { useState } from "react";
import axios from "axios";

const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

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

  const runWhatIf = async () => {
    if (!prediction) {
      alert("Run Demo Scenario or Video Intelligence first.");
      return;
    }

    setLoading(true);

    try {
      const response = await axios.post(`${API}/what-if`, {
        original_scenario: {
          impact_score: prediction.impact_score,
          closure_probability: prediction.closure_probability,
          priority: prediction.priority,
          expected_crowd_size: 18000,
          event_duration_hours: prediction.expected_duration_hours_p50,
          peak_hour: true,
          nearby_sensitive_zone: true,
        },
        modifications: {
          expected_crowd_size: Number(form.expected_crowd_size),
          event_duration_hours: Number(form.event_duration_hours),
          impact_score: Number(form.impact_score),
          closure_probability: Number(form.closure_probability),
          priority: form.priority,
          peak_hour: Boolean(form.peak_hour),
          nearby_sensitive_zone: Boolean(form.nearby_sensitive_zone),
        },
      });

      setResult(response.data);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const originalInput = {
    expected_crowd_size: 18000,
    event_duration_hours: prediction?.expected_duration_hours_p50 || 0,
    impact_score: prediction?.impact_score || 0,
    closure_probability: prediction?.closure_probability || 0,
    peak_hour: true,
    nearby_sensitive_zone: true,
  };

  const modifiedInput = {
    expected_crowd_size: Number(form.expected_crowd_size),
    event_duration_hours: Number(form.event_duration_hours),
    impact_score: Number(form.impact_score),
    closure_probability: Number(form.closure_probability),
    peak_hour: form.peak_hour ? 1 : 0,
    nearby_sensitive_zone: form.nearby_sensitive_zone ? 1 : 0,
  };

  return (
    <div className="card">
      <h2>What-If Simulator</h2>

      <p>
        Manually change traffic conditions and compare every modified parameter
        against the current scenario.
      </p>

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

        <label className="field">
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

      <InputComparisonCharts
        original={originalInput}
        modified={modifiedInput}
      />

      <button className="primary-btn" onClick={runWhatIf} disabled={loading}>
        {loading ? "Running..." : "Run What-If"}
      </button>

      {result && (
        <div className="whatif-result">
          <h3>What-If Result</h3>

          <div className="comparison-strip">
            <div>
              <span>Original Risk</span>
              <strong>{result.comparison.risk_level_change.from}</strong>
            </div>

            <div>
              <span>Modified Risk</span>
              <strong>{result.comparison.risk_level_change.to}</strong>
            </div>
          </div>

          <GroupedBars
            title="Resource Deployment Change"
            rows={[
              [
                "Manpower",
                result.original_plan.manpower,
                result.modified_plan.manpower,
                60,
              ],
              [
                "Barricades",
                result.original_plan.barricades,
                result.modified_plan.barricades,
                40,
              ],
              [
                "Patrol",
                result.original_plan.patrol_units,
                result.modified_plan.patrol_units,
                15,
              ],
              [
                "Emergency",
                result.original_plan.emergency_units,
                result.modified_plan.emergency_units,
                8,
              ],
            ]}
          />
        </div>
      )}
    </div>
  );
}

function InputComparisonCharts({ original, modified }) {
  const rows = [
    {
      label: "Crowd Size",
      original: original.expected_crowd_size,
      modified: modified.expected_crowd_size,
      max: 50000,
    },
    {
      label: "Duration",
      original: original.event_duration_hours,
      modified: modified.event_duration_hours,
      max: 24,
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
      label: "Peak Hour",
      original: original.peak_hour ? 1 : 0,
      modified: modified.peak_hour ? 1 : 0,
      max: 1,
      boolean: true,
    },
    {
      label: "Sensitive Zone",
      original: original.nearby_sensitive_zone ? 1 : 0,
      modified: modified.nearby_sensitive_zone ? 1 : 0,
      max: 1,
      boolean: true,
    },
  ];

  return (
    <div className="parameter-chart-section">
      <h3>Manual Parameter Comparison</h3>

      <div className="parameter-chart-grid">
        {rows.map((row) => (
          <ParameterMiniChart key={row.label} row={row} />
        ))}
      </div>
    </div>
  );
}

function ParameterMiniChart({ row }) {
  const originalWidth = Math.min((row.original / row.max) * 100, 100);
  const modifiedWidth = Math.min((row.modified / row.max) * 100, 100);

  const originalValue = row.boolean
    ? row.original
      ? "Yes"
      : "No"
    : `${row.original}${row.suffix || ""}`;

  const modifiedValue = row.boolean
    ? row.modified
      ? "Yes"
      : "No"
    : `${row.modified}${row.suffix || ""}`;

  return (
    <div className="parameter-chart-card">
      <div className="parameter-chart-head">
        <strong>{row.label}</strong>
        <span>
          {originalValue} → {modifiedValue}
        </span>
      </div>

      <div className="mini-bar-line">
        <span>Original</span>
        <div className="bar-track">
          <div
            className="bar-fill original-bar"
            style={{ width: `${originalWidth}%` }}
          />
        </div>
        <strong>{originalValue}</strong>
      </div>

      <div className="mini-bar-line">
        <span>Modified</span>
        <div className="bar-track">
          <div
            className="bar-fill modified-bar"
            style={{ width: `${modifiedWidth}%` }}
          />
        </div>
        <strong>{modifiedValue}</strong>
      </div>
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

function GroupedBars({ title, rows }) {
  return (
    <div className="group-chart">
      <h3>{title}</h3>

      <div className="chart-legend">
        <span className="legend-original">Original</span>
        <span className="legend-modified">Modified</span>
      </div>

      {rows.map(([label, original, modified, max]) => (
        <div className="comparison-row" key={label}>
          <div className="comparison-label">
            <strong>{label}</strong>
            <span>
              {original} → {modified}
            </span>
          </div>

          <div className="comparison-bars">
            <div className="bar-line">
              <span>Original</span>
              <div className="bar-track">
                <div
                  className="bar-fill original-bar"
                  style={{ width: `${Math.min((original / max) * 100, 100)}%` }}
                />
              </div>
              <strong>{original}</strong>
            </div>

            <div className="bar-line">
              <span>Modified</span>
              <div className="bar-track">
                <div
                  className="bar-fill modified-bar"
                  style={{ width: `${Math.min((modified / max) * 100, 100)}%` }}
                />
              </div>
              <strong>{modified}</strong>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}