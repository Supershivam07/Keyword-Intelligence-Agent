from zhipuai import ZhipuAI
from config import GLM_API_KEY, GLM_MODEL


class GLMClient:
    """
    Used as AGENT brain.
    """

    def __init__(self):
        if not GLM_API_KEY:
            raise ValueError("GLM_API_KEY missing")

        self.client = ZhipuAI(api_key=GLM_API_KEY)
        self.model = GLM_MODEL

    def reason(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()