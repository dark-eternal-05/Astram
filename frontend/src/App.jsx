import { useState } from "react";
import "./App.css";

import DemoScenario from "./components/DemoScenario";
import VideoInput from "./components/VideoInput";
import ForecastPanel from "./components/ForecastPanel";
import ResourcePanel from "./components/ResourcePanel";
import DiversionPanel from "./components/DiversionPanel";
import HistoricalPanel from "./components/HistoricalPanel";
import WhatIfPanel from "./components/WhatIfPanel";
import FeedbackPanel from "./components/FeedbackPanel";

export default function App() {
  const [inputMode, setInputMode] = useState("demo");

  const [prediction, setPrediction] = useState(null);
  const [resourcePlan, setResourcePlan] = useState(null);
  const [diversionPlan, setDiversionPlan] = useState(null);
  const [similarEvents, setSimilarEvents] = useState(null);
  const [videoEvent, setVideoEvent] = useState(null);

  const sharedProps = {
    setPrediction,
    setResourcePlan,
    setDiversionPlan,
    setSimilarEvents,
    setVideoEvent,
  };

  return (
    <main className="page">
      <section className="hero">
        <div>
          <span className="badge">ASTRaM Traffic Operations Center</span>
          <h1>Traffic Event Detection & Resource Command</h1>
          <p>
            Choose demo mode for reliable presentation or video intelligence mode
            to let the agent identify traffic events from uploaded location video.
          </p>
        </div>
      </section>

      <section className="metrics">
        <Metric label="Input Mode" value={inputMode === "demo" ? "Demo" : "Video"} />
        <Metric label="Detected Event" value={videoEvent?.event_cause ?? "—"} />
        <Metric
          label="Traffic Density"
          value={videoEvent ? `${videoEvent.traffic_density}%` : "—"}
        />
        <Metric label="Impact Score" value={prediction?.impact_score ?? "—"} />
      </section>

      <section className="input-mode-card">
        <h2>Select Input Source</h2>

        <div className="mode-selector">
          <button
            className={inputMode === "demo" ? "mode-btn active" : "mode-btn"}
            onClick={() => setInputMode("demo")}
          >
            Demo Scenario
          </button>

          <button
            className={inputMode === "video" ? "mode-btn active" : "mode-btn"}
            onClick={() => setInputMode("video")}
          >
            Video Intelligence
          </button>
        </div>
      </section>

      <section className="dashboard-grid">
        {inputMode === "demo" ? (
          <DemoScenario {...sharedProps} />
        ) : (
          <VideoInput {...sharedProps} />
        )}

        <ForecastPanel data={prediction} videoEvent={videoEvent} />
        <ResourcePanel data={resourcePlan} />
        <DiversionPanel data={diversionPlan} />
        <HistoricalPanel data={similarEvents} />
        <WhatIfPanel prediction={prediction} />
        <FeedbackPanel />
      </section>
    </main>
  );
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}