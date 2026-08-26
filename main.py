# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from logicengine import LogicEngine, PatientPayload

app = FastAPI(
    title="HFrEF AI Agent Engine - Stage 1 & Stage 2",
    version="2.0.0"
)

# Enable CORS for Front-End UI Canvas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/evaluate-patient")
def evaluate_patient(payload: PatientPayload):
    """Stage 1: Execute Deterministic 7-Step Logic Engine & Save to DynamoDB."""
    return LogicEngine.run_7_steps(payload)