# rag.py
# Stage 2: RAG Retrieval Engine using Amazon Bedrock & OpenSearch Serverless / Local Mock

import os
from typing import List

# Mock Guideline Knowledge Base for Local Testing / Prototype Stage
MOCK_ACC_AHA_GUIDELINES = {
    "copd": "ACC/AHA HFrEF Guidelines Section 7.3: In patients with concurrent COPD or Asthma, cardioselective Beta-1 blockers (Bisoprolol, Metoprolol Succinate) are strongly preferred over non-selective agents (Carvedilol) to prevent bronchospasm.",
    "arni": "ACC/AHA HFrEF Guidelines Section 4.1: Sacubitril/Valsartan (ARNI) requires SBP >= 100 mmHg, K+ < 5.5 mEq/L, and eGFR >= 30 mL/min/1.73m2 prior to initiation or uptitration.",
    "mra": "ACC/AHA HFrEF Guidelines Section 5.2: Spironolactone/Eplerenone should be held if Serum K+ > 5.0 mEq/L or eGFR < 30 mL/min/1.73m2.",
    "sglt2": "ACC/AHA HFrEF Guidelines Section 6.1: SGLT2 inhibitors (Dapagliflozin/Empagliflozin) are recommended for all HFrEF patients with eGFR >= 20 mL/min/1.73m2 regardless of diabetes status.",
    "fluid": "ACC/AHA HFrEF Guidelines Section 3.1: Hypervolemia (>35% thoracic impedance fluid) requires loop diuretic escalation before uptitrating disease-modifying agents."
}

class GuidelineRAG:
    """RAG Retriever class wrapping vector retrieval (Amazon OpenSearch or local mock)."""
    def __init__(self, use_aws_bedrock: bool = False):
        self.use_aws_bedrock = use_aws_bedrock

    def query_guidelines(self, query: str) -> str:
        """Retrieves matching clinical guideline chunks based on query terms."""
        results = []
        query_lower = query.lower()
        for key, text in MOCK_ACC_AHA_GUIDELINES.items():
            if key in query_lower or any(term in query_lower for term in key.split()):
                results.append(text)
        
        if not results:
            return "Standard ACC/AHA GDMT Guidelines: Ensure SBP > 90 mmHg, K+ < 5.0 mEq/L, and monitor 24-hr parameter drift."
        
        return "\n\n".join(results)

# Global Instance
rag_engine = GuidelineRAG()
