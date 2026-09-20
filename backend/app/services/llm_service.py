from openai import AsyncOpenAI
from app.config import settings


class LLMService:
    def __init__(self):
        kwargs = {"api_key": settings.OPENAI_API_KEY}
        if settings.OPENAI_BASE_URL:
            kwargs["base_url"] = settings.OPENAI_BASE_URL
        self.client = AsyncOpenAI(**kwargs)

    async def generate_grounded_answer(
        self, prompt: str, system_prompt: str = None
    ) -> str:
        if not system_prompt:
            system_prompt = (
                "You are RAGForge, an expert AI research assistant. Your task is to answer user "
                "questions strictly using the retrieved context provided. You MUST ground every claim "
                "with inline citations such as [1], [2]."
            )

        response = await self.client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip()