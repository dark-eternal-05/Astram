export default function ResourcePanel({
  data,
}) {
  if (!data)
    return (
      <div className="card">
        No resource plan.
      </div>
    );

  return (
    <div className="card">
      <h2>Resource Deployment</h2>

      <Info
        title="Manpower"
        value={data.manpower}
      />

      <Info
        title="Barricades"
        value={data.barricades}
      />

      <Info
        title="Patrol Units"
        value={data.patrol_units}
      />

      <Info
        title="Emergency Units"
        value={data.emergency_units}
      />

      <Info
        title="Risk Level"
        value={data.risk_level}
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