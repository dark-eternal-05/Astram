export default function HistoricalPanel({
  data,
}) {
  if (!data)
    return (
      <div className="card">
        No history.
      </div>
    );

  return (
    <div className="card">
      <h2>Historical Events</h2>

      {data.matches?.map(
        (event) => (
          <div
            className="event-item"
            key={event.event_id}
          >
            <strong>
              {event.event_id}
            </strong>

            <p>
              {event.summary}
            </p>
          </div>
        )
      )}
    </div>
  );
}