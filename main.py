# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from logicengine import LogicEngine, PatientPayload
from rag import rag_engine

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

class ChatPayload(BaseModel):
    patient_payload: PatientPayload
    question: str

@app.post("/api/v1/evaluate-patient")
def evaluate_patient(payload: PatientPayload):
    """Stage 1: Execute Deterministic 7-Step Logic Engine & Save to DynamoDB."""
    return LogicEngine.run_7_steps(payload)

@app.post("/api/v1/chat")
def chat_with_agent(payload: ChatPayload):
    """Stage 2: Combine Stage 1 deterministic results with RAG guideline retrieval."""
    stage1_result = LogicEngine.run_7_steps(payload.patient_payload)
    retrieved_guidelines = rag_engine.query_guidelines(payload.question)
    
    response_text = (
        f"Based on the Stage 1 evaluation for Patient {payload.patient_payload.patient_id}, "
        f"the fluid volume status is classified as **{stage1_result['fluid_status']}** "
        f"with emergency override triggered: {stage1_result['emergency_triggered']}.\n\n"
        f"**Engine Recommended Actions:**\n" +
        "\n".join([f"- **{k.upper()}**: {v}" for k, v in stage1_result['actions'].items()]) +
        f"\n\n**Relevant ACC/AHA Guideline Evidence (RAG):**\n{retrieved_guidelines}"
    )
    
    return {
        "patient_id": payload.patient_payload.patient_id,
        "stage1_outcome": stage1_result,
        "response": response_text
    }
