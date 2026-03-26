import os
import json
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """
    Stable production Gemini client.
    Provides BOTH raw text + streaming helpers.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in environment")

        self.client = genai.Client(api_key=self.api_key)

        # ✅ Free tier safe model
        self.model_name = "gemini-2.5-flash"

    # =========================================================
    # 🧠 NORMAL GENERATION (unchanged)
    # =========================================================
    def generate(self, prompt: str, use_search: bool = True) -> str:
        try:
            tools = []
            if use_search:
                tools = [
                    types.Tool(googleSearch=types.GoogleSearch()),
                    # url_context removed — caused 400 INVALID_ARGUMENT when URLs exceeded Gemini limit
                ]

            config = types.GenerateContentConfig(
                temperature=0.2,
                tools=tools if tools else None,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            if not response or not response.text:
                return ""

            return response.text.strip()

        except Exception as e:
            print(f"❌ Gemini search error: {e}")
            raise

    # =========================================================
    # 🚀 STREAMING GENERATION (NEW — SAFE)
    # =========================================================
    def generate_stream(self, prompt: str, use_search: bool = True):
        """
        Streams text chunks from Gemini.
        DOES NOT affect existing logic.
        """

        try:
            tools = []
            if use_search:
                tools = [
                    types.Tool(googleSearch=types.GoogleSearch()),
                    # url_context removed — caused 400 INVALID_ARGUMENT when URLs exceeded Gemini limit
                ]

            config = types.GenerateContentConfig(
                temperature=0.2,
                tools=tools if tools else None,
            )

            stream = self.client.models.generate_content_stream(
                model=self.model_name,
                contents=prompt,
                config=config,
            )

            for chunk in stream:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"❌ Gemini streaming error: {e}")
            yield "\n❌ Streaming failed.\n"