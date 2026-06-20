import { useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

export default function VideoInput({
  setPrediction,
  setResourcePlan,
  setDiversionPlan,
  setSimilarEvents,
  setVideoEvent,
}) {
  const [video, setVideo] = useState(null);

  const [preview, setPreview] = useState(null);

  const [loading, setLoading] = useState(false);

  const [region, setRegion] =
    useState("Silk Board Junction");

  const uploadVideo = async () => {
    if (!video) {
      alert("Upload a video.");
      return;
    }

    setLoading(true);

    try {
      const form = new FormData();

      form.append("video", video);

      form.append(
        "region_name",
        region
      );

      form.append(
        "corridor",
        "Hosur Road"
      );

      form.append(
        "zone",
        "South Zone 1"
      );

      form.append(
        "junction",
        "SilkBoardJunc"
      );

      form.append("hour", 8);

      form.append(
        "day_of_week",
        1
      );

      form.append("month", 3);

      const response =
        await axios.post(
          `${API}/video-pipeline`,
          form
        );

      setVideoEvent(
        response.data.video_event
      );

      setPrediction(
        response.data.prediction
      );

      setResourcePlan(
        response.data.resource_plan
      );

      setDiversionPlan(
        response.data.diversion_plan
      );

      setSimilarEvents(
        response.data.similar_events
      );
    } catch (err) {
      alert(
        err.response?.data?.detail ||
          err.message
      );
    }

    setLoading(false);
  };

  return (
    <div className="card">
      <h2>Video Intelligence</h2>

      <input
        value={region}
        onChange={(e) =>
          setRegion(
            e.target.value
          )
        }
      />

      <input
        type="file"
        accept="video/*"
        onChange={(e) => {
          const file =
            e.target.files[0];

          setVideo(file);

          setPreview(
            URL.createObjectURL(
              file
            )
          );
        }}
      />

      {preview && (
        <video
          controls
          src={preview}
          className="video-preview"
        />
      )}

      <button
        className="primary-btn"
        onClick={uploadVideo}
      >
        {loading
          ? "Analyzing..."
          : "Run ASTRaM"}
      </button>
    </div>
  );
}