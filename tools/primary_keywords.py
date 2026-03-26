# tools/primary_keywords.py
from typing import List, Dict, Any
from llm_clients.gemini_client import GeminiClient


def generate_primary_keywords(topic: str, urls: List[str]) -> Dict[str, Any]:
    """
    Given topic and list of URLs, return primary keywords JSON.
    Note: urls can be pre-cleaned.
    """
    gemini = GeminiClient()

    # take up to 10 URLs (the agent expects a small batch)
    urls_text = "\n".join(urls[:10])

    prompt = f"""
You are an elite SEO keyword strategist.

TOPIC:
{topic}

Analyze the following high-ranking pages:

{urls_text}

TASK:
Extract the MOST IMPORTANT high-ranking SEO keywords
that are responsible for these pages ranking on Google.

RULES:
- Focus on high-intent keywords
- Remove duplicates
- Keep keywords concise
- Return JSON only

OUTPUT FORMAT:
{{
  "high_ranking_keywords": ["keyword1", "keyword2", "..."]
}}
"""

    return gemini.generate_json(prompt)
