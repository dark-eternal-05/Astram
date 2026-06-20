export default function WhatIfPanel({
  prediction,
}) {
  return (
    <div className="card">
      <h2>What If</h2>

      <p>
        Existing what-if logic
        can be reused here.
      </p>

      {prediction && (
        <div>
          Base Impact Score:

          {prediction.impact_score}
        </div>
      )}
    </div>
  );
}