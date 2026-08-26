# main.py
# Stage 2 + API Layer: FastAPI REST & Interactive RAG Chatbot Endpoint

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from logicengine import LogicEngine, PatientPayload
from rag import rag_engine

app = FastAPI(
    title="HFrEF AI Agent Platform - 2-Stage Hybrid Architecture",
    description="Combines a deterministic 7-step clinical logic engine with an interactive RAG chatbot.",
    version="2.0.0"
)

class ChatQueryRequest(BaseModel):
    patient_payload: PatientPayload
    question: str

@app.post("/api/v1/evaluate-patient")
def evaluate_patient(payload: PatientPayload):
    """Stage 1: Execute Deterministic 7-Step Logic Engine."""
    result = LogicEngine.run_7_steps(payload)
    return result

@app.post("/api/v1/chat")
def interactive_rag_chat(request: ChatQueryRequest):
    """Stage 2: RAG Chatbot using Stage 1 Outcome as Context."""
    # 1. Run Stage 1 Engine to get authoritative ground truth
    stage1_outcome = LogicEngine.run_7_steps(request.patient_payload)
    
    # 2. Retrieve relevant guidelines via RAG
    guideline_context = rag_engine.query_guidelines(request.question)
    
    # 3. Formulate Context-Aware Explanation
    if stage1_outcome["emergency_triggered"]:
        response_text = (
            f"ALERT: For Patient {request.patient_payload.patient_id}, an emergency safety gate was tripped. "
            "Automated titration is currently halted for clinician review."
        )
    else:
        actions_str = ", ".join([f"{k.upper()}: {v}" for k, v in stage1_outcome["actions"].items()])
        response_text = (
            f"### Stage 1 Decision Outcome for Patient {request.patient_payload.patient_id}\n"
            f"- **Fluid Status**: {stage1_outcome['fluid_status']}\n"
            f"- **Recommended Actions**: {actions_str}\n\n"
            f"### Relevant ACC/AHA Guideline Citation\n"
            f"{guideline_context}\n\n"
            f"### Clinical Explanation\n"
            f"Regarding your query ('{request.question}'): The recommendation directly reflects the patient's "
            f"current telemetry (SBP: {request.patient_payload.telemetry.sbp} mmHg, K+: {request.patient_payload.labs.k} mEq/L) "
            f"and clinical history ({', '.join(request.patient_payload.comorbidities)})."
        )
        
    return {
        "patient_id": request.patient_payload.patient_id,
        "question": request.question,
        "stage1_outcome": stage1_outcome,
        "rag_guideline_context": guideline_context,
        "response": response_text
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
