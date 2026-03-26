import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GLM_API_KEY = os.getenv("GLM_API_KEY")

# models
GEMINI_MODEL = "gemini-2.5-flash"
GLM_MODEL = "glm-4.7-flash"