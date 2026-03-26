from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from llm_clients.gemini_client import GeminiClient

app = FastAPI()
gemini = GeminiClient()


@app.get("/stream")
def stream_topic(topic: str):
    """
    Safe streaming endpoint.
    Does NOT affect existing UI or FastAPI routes.
    """

    prompt = f"""
Explain the topic clearly and professionally.

TOPIC: {topic}
"""

    def generator():
        yield "🤖 Analyzing...\n\n"

        try:
            for chunk in gemini.generate_stream(
                prompt,
                use_search=False,
            ):
                yield chunk
        except Exception as e:
            yield f"\n\n❌ Error: {str(e)}"

    return StreamingResponse(generator(), media_type="text/plain")