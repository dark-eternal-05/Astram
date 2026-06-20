export default function ForecastPanel({
  data,
  videoEvent,
}) {
  if (!data)
    return (
      <div className="card">
        No forecast yet.
      </div>
    );

  return (
    <div className="card">
      <h2>Forecast</h2>

      <Info
        title="Detected Event"
        value={
          videoEvent?.event_cause
        }
      />

      <Info
        title="Impact Score"
        value={data.impact_score}
      />

      <Info
        title="Priority"
        value={data.priority}
      />

      <Info
        title="Closure Risk"
        value={`${Math.round(
          data.closure_probability *
            100
        )}%`}
      />

      <Info
        title="Duration P50"
        value={`${data.expected_duration_hours_p50} hrs`}
      />

      <Info
        title="Duration P90"
        value={`${data.expected_duration_hours_p90} hrs`}
      />
    </div>
  );
}

function Info({
  title,
  value,
}) {
  return (
    <div className="info-item">
      <span>{title}</span>

      <strong>{value}</strong>
    </div>
  );
}