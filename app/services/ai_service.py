from app.core.config import settings

class AIService:
    def __init__(self):
        self.system_name = settings.PROJECT_NAME

    async def process_message(self, message: str) -> str:
        cleaned_message = self._clean_message(message)
        response = await self._generate_response(cleaned_message)
        return response

    def _clean_message(self, message: str) -> str:
        return message.strip()

    async def _generate_response(self, message: str) -> str:
        # simulate async operation
        return f"{self.system_name} received: {message}"


ai_service = AIService()