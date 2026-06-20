export default function DiversionPanel({
  data,
}) {
  if (!data)
    return (
      <div className="card">
        No diversion plan.
      </div>
    );

  return (
    <div className="card">
      <h2>Diversion</h2>

      <Info
        title="Source"
        value={data.source}
      />

      <Info
        title="Destination"
        value={
          data.destination
        }
      />

      <Info
        title="Delay"
        value={`${data.recommended_route.total_delay_minutes} mins`}
      />

      <div className="route-box">
        {data.recommended_route.route.map(
          (r) => (
            <span key={r}>
              {r}
            </span>
          )
        )}
      </div>
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