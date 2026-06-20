import axios from "axios";

const API = "http://127.0.0.1:8000";

export default function DemoScenario({
  setPrediction,
  setResourcePlan,
  setDiversionPlan,
  setSimilarEvents,
  setVideoEvent,
}) {
  const runDemo = async () => {
    try {
      const prediction = await axios.post(`${API}/predict`, {
        event_cause: "construction",
        corridor: "Hosur Road",
        zone: "South Zone 1",
        junction: "SilkBoardJunc",
        hour: 7,
        day_of_week: 1,
        month: 3,
        is_planned: false,
        involves_heavy_vehicle: false,
        is_authenticated: true,
      });

      setPrediction(prediction.data);

      setVideoEvent({
        event_cause: "construction",
        confidence: 1,
        traffic_density: 78,
        average_speed_kmph: 18,
        expected_crowd_size: 18000,
      });

      const optimize = await axios.post(`${API}/optimize`, {
        impact_score: prediction.data.impact_score,
        closure_probability: prediction.data.closure_probability,
        priority: prediction.data.priority,
        expected_crowd_size: 18000,
        event_duration_hours: prediction.data.expected_duration_hours_p50,
        peak_hour: true,
        nearby_sensitive_zone: true,
      });

      setResourcePlan(optimize.data);

      const diversion = await axios.post(`${API}/diversion`, {
        source: "Central Stadium Road",
        destination: "City Exit Road",
        blocked_roads: ["Market Junction"],
      });

      setDiversionPlan(diversion.data);

      const history = await axios.post(`${API}/similar-events`, {
        query_text: "Road construction during peak hours with congestion risk",
        top_k: 3,
      });

      setSimilarEvents(history.data);
    } catch (err) {
      alert(err.response?.data?.detail || err.message);
    }
  };

  return (
    <div className="card">
      <h2>Demo Scenario</h2>

      <p>Runs a stable predefined traffic event for judge-facing demonstrations.</p>

      <div className="info-item">
        <span>Scenario</span>
        <strong>Construction near Silk Board Junction</strong>
      </div>

      <div className="info-item">
        <span>Purpose</span>
        <strong>Reliable fallback when video upload is not needed</strong>
      </div>

      <button className="primary-btn" onClick={runDemo}>
        Run Demo Scenario
      </button>
    </div>
  );
}