from google import genai
from app.intelligence.config import GEMINI_API_KEY

client = genai.Client(api_key=GEMINI_API_KEY)

async def ask_gemini(prompt: str) -> str:
    response = await client.aio.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text