from google import genai
from core.app.core.config import settings

client = genai.Client(api_key=settings.GEMINI_API_KEY)

async def ask_gemini(prompt: str) -> str:
    response = await client.aio.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    return response.text