export default function FeedbackPanel() {
  return (
    <div className="card">
      <h2>Feedback</h2>

      <textarea
        placeholder="Operator notes..."
      />

      <button className="primary-btn">
        Submit
      </button>
    </div>
  );
}