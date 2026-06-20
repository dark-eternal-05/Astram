from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from app.agents.signal_structuring_agent import SignalStructuringAgent
from app.agents.video_event_agent import VideoEventAgent
from app.schemas.signal_schema import RawSignalInput
from app.validators.csv_validator import CSVValidator
from app.forecasting.astram_model_wrapper import (
    ASTRaMForecastInput,
    ASTRaMModelWrapper,
)
from app.optimization.resource_optimizer import (
    OptimizationInput,
    ResourceOptimizer,
)
from app.routing.diversion_planner import DiversionInput, DiversionPlanner
from app.knowledge.historical_memory import HistoricalMemory
from app.simulation.what_if_simulator import WhatIfInput, WhatIfSimulator

app = FastAPI(
    title="ASTRaM Backend",
    description="Agentic Traffic Resource and Mobility System backend",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://YOUR-VERCEL-APP.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = Path("app/data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

signal_agent = SignalStructuringAgent()
video_event_agent = VideoEventAgent()
csv_validator = CSVValidator()
resource_optimizer = ResourceOptimizer()
diversion_planner = DiversionPlanner()
historical_memory = HistoricalMemory()
what_if_simulator = WhatIfSimulator()

try:
    forecasting_model = ASTRaMModelWrapper()
    model_load_error = None
except Exception as exc:
    forecasting_model = None
    model_load_error = repr(exc)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ASTRaM Backend",
        "version": "0.3.0",
        "model_loaded": forecasting_model is not None,
        "model_load_error": model_load_error,
    }


@app.post("/structure-signal")
def structure_signal(raw_signal: RawSignalInput):
    try:
        structured_signal = signal_agent.structure(raw_signal)
        csv_row = csv_validator.to_csv_dict(structured_signal)

        return {
            "structured_signal": structured_signal.model_dump(),
            "csv_row": csv_row,
        }

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/analyze-video-event")
async def analyze_video_event(
    video: UploadFile = File(...),
):
    try:
        suffix = Path(video.filename).suffix or ".mp4"
        saved_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"

        with saved_path.open("wb") as buffer:
            buffer.write(await video.read())

        inference = video_event_agent.analyze(str(saved_path))

        return {
            "status": "success",
            "video_event": inference.model_dump(),
        }

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/video-pipeline")
async def video_pipeline(
    video: UploadFile = File(...),
    region_name: str = Form("Unknown Region"),
    corridor: str = Form("Non-corridor"),
    zone: str = Form("Unzoned"),
    junction: str = Form("UnknownJunction"),
    hour: int = Form(7),
    day_of_week: int = Form(1),
    month: int = Form(3),
):
    if forecasting_model is None:
        raise HTTPException(
            status_code=500,
            detail="ASTRaM model bundle not found. Place astram_model_bundle.joblib inside backend/models.",
        )

    try:
        suffix = Path(video.filename).suffix or ".mp4"
        saved_path = UPLOAD_DIR / f"{uuid4().hex}{suffix}"

        with saved_path.open("wb") as buffer:
            buffer.write(await video.read())

        video_event = video_event_agent.analyze(str(saved_path))

        predict_input = ASTRaMForecastInput(
            event_cause=video_event.event_cause,
            corridor=corridor,
            zone=zone,
            junction=junction,
            hour=hour,
            day_of_week=day_of_week,
            month=month,
            is_planned=video_event.is_planned,
            involves_heavy_vehicle=video_event.involves_heavy_vehicle,
            is_authenticated=video_event.is_authenticated,
        )

        prediction = forecasting_model.predict(predict_input)

        optimize_input = OptimizationInput(
            impact_score=prediction.impact_score,
            closure_probability=prediction.closure_probability,
            priority=prediction.priority,
            expected_crowd_size=video_event.expected_crowd_size,
            event_duration_hours=prediction.expected_duration_hours_p50,
            peak_hour=7 <= hour <= 10 or 17 <= hour <= 21,
            nearby_sensitive_zone=video_event.traffic_density >= 75,
        )

        resource_plan = resource_optimizer.optimize(optimize_input)

        diversion_plan = diversion_planner.plan(
            DiversionInput(
                source="Central Stadium Road",
                destination="City Exit Road",
                blocked_roads=["Market Junction"]
                if prediction.closure_predicted
                else [],
            )
        )

        similar_events = historical_memory.find_similar_events(
            query_text=(
                f"{video_event.event_cause} near {region_name} "
                f"with traffic density {video_event.traffic_density}%"
            ),
            top_k=3,
        )

        return {
            "status": "success",
            "source": "video_event_agent",
            "region_name": region_name,
            "video_event": video_event.model_dump(),
            "prediction": prediction.model_dump(),
            "resource_plan": resource_plan.model_dump(),
            "diversion_plan": diversion_plan.model_dump(),
            "similar_events": similar_events,
        }

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/predict")
def predict(data: ASTRaMForecastInput):
    if forecasting_model is None:
        raise HTTPException(
            status_code=500,
            detail="ASTRaM model bundle not found. Place astram_model_bundle.joblib inside backend/models.",
        )

    try:
        prediction = forecasting_model.predict(data)
        return prediction.model_dump()

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/optimize")
def optimize(data: OptimizationInput):
    try:
        plan = resource_optimizer.optimize(data)
        return plan.model_dump()

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/diversion")
def diversion(data: DiversionInput):
    try:
        plan = diversion_planner.plan(data)
        return plan.model_dump()

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/similar-events")
def similar_events(payload: dict):
    try:
        query_text = payload.get("query_text")
        top_k = int(payload.get("top_k", 3))

        if not query_text:
            raise ValueError("query_text is required.")

        matches = historical_memory.find_similar_events(
            query_text=query_text,
            top_k=top_k,
        )

        return {
            "query_text": query_text,
            "matches": matches,
        }

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/what-if")
def what_if(data: WhatIfInput):
    try:
        result = what_if_simulator.run(data)
        return result.model_dump()

    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/feedback")
def feedback(payload: dict):
    return {
        "status": "received",
        "message": "Feedback storage will be implemented in Step 12.",
        "feedback": payload,
    }


@app.post("/retrain")
def retrain():
    return {
        "status": "not_started",
        "message": "Retraining and ChromaDB update will be implemented in Step 13.",
    }