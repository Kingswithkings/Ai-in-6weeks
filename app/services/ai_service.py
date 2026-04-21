from openai import AsyncOpenAI
from app.core.config import settings


class AIService:
    def __init__(self):
        self.system_name = settings.PROJECT_NAME
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def process_message(self, message: str) -> str:
        cleaned_message = self._clean_message(message)
        response = await self._generate_response(cleaned_message)
        return response

    def _clean_message(self, message: str) -> str:
        return message.strip()

    async def _generate_response(self, message: str) -> str:
        if not settings.OPENAI_API_KEY:
            return "OpenAI API key is missing. Add it to your .env file."

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful AI assistant for Kings. "
                            "Give clear, concise, and useful responses."
                        ),
                    },
                    {"role": "user", "content": message},
                ],
                temperature=0.7,
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error while calling OpenAI: {str(e)}"


ai_service = AIService()