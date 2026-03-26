from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json

from agent.keyword_agent import KeywordAgent

# =========================================================
# FastAPI app
# =========================================================
app = FastAPI(
    title="Keyword Intelligence API",
    description="AI-powered high-ranking keyword extractor",
    version="1.0.0",
)

# =========================================================
# Request schema
# =========================================================
class TopicRequest(BaseModel):
    topic: str


# =========================================================
# Health check endpoint (optional but professional)
# =========================================================
@app.get("/")
def health_check():
    return {"status": "API is running 🚀"}


# =========================================================
# MAIN ENDPOINT (your mentor wants this)
# =========================================================
@app.post("/analyze-topic")
def analyze_topic(request: TopicRequest):
    try:
        topic = request.topic.strip()

        if not topic:
            raise HTTPException(status_code=400, detail="Topic cannot be empty")

        agent = KeywordAgent()
        result = agent.run(topic)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
