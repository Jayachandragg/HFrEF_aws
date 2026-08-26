# rag.py
# Stage 2: Knowledge Base RAG Engine using AWS Bedrock

import boto3
import os
from botocore.exceptions import ClientError

# Read Bedrock Knowledge Base ID from environment variables or use fallback
BEDROCK_KB_ID = os.getenv("BEDROCK_KB_ID", "YOUR_KNOWLEDGE_BASE_ID")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

class GuidelineRAG:
    """RAG Retrieval Engine interacting with AWS Bedrock Knowledge Base."""

    def __init__(self):
        try:
            self.bedrock_agent_runtime = boto3.client(
                service_name='bedrock-agent-runtime',
                region_name=AWS_REGION
            )
            self.is_connected = True
            print("[Info] AWS Bedrock Agent Runtime initialized successfully.")
        except Exception as e:
            print(f"[Warning] Bedrock client initialization skipped/failed: {e}. Running in local mock fallback mode.")
            self.is_connected = False

    def query_guidelines(self, query: str) -> str:
        """Queries Bedrock Knowledge Base vector store for ACC/AHA HFrEF guidelines."""
        
        # If running locally without Bedrock KB configured yet, return fallback guideline context
        if not self.is_connected or BEDROCK_KB_ID == "YOUR_KNOWLEDGE_BASE_ID":
            return (
                "ACC/AHA HFrEF Guideline Section 7.3 (GDMT Titration):\n"
                "1. Beta-Blockers: In patients with reactive airway disease (COPD/Asthma), "
                "cardioselective Beta-1 blockers (e.g., Bisoprolol or Metoprolol Succinate) "
                "are strongly recommended over non-selective agents like Carvedilol.\n"
                "2. ARNI/RAASi: Sacubitril/Valsartan uptitration requires SBP >= 100 mmHg, "
                "Serum K+ < 5.5 mEq/L, and eGFR >= 30 mL/min/1.73m2.\n"
                "3. Loop Diuretics: Increase dose during hypervolemic (WET) states; maintain during normovolemic (DRY) states."
            )

        try:
            # Retrieve top 3 relevant chunks from AWS Bedrock OpenSearch Vector Store
            response = self.bedrock_agent_runtime.retrieve(
                knowledgeBaseId=BEDROCK_KB_ID,
                retrievalQuery={'text': query},
                retrievalConfiguration={
                    'vectorSearchConfiguration': {
                        'numberOfResults': 3
                    }
                }
            )

            results = response.get('retrievalResults', [])
            if not results:
                return "No matching clinical guidelines found in Knowledge Base for this query."

            # Format retrieved text chunks with source tags
            guideline_chunks = []
            for r in results:
                source_uri = r.get('location', {}).get('s3Location', {}).get('uri', 'ACC/AHA Guideline KB')
                text = r.get('content', {}).get('text', '')
                guideline_chunks.append(f"[Source: {source_uri}]\n{text}")

            return "\n\n".join(guideline_chunks)

        except ClientError as e:
            print(f"[AWS Bedrock Error] Query failed: {e}")
            return f"Guideline retrieval error: {e.response['Error']['Message']}"

# Singleton instance
rag_engine = GuidelineRAG()