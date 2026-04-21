class AIService:
    def __init__(self):
        self.system_name = "Kings AI Service"

    def process_message(self, message: str) -> str:
        """
        Main service method for handling user messages.
        Later this can call OpenAI, RAG pipelines, tools, or agents.
        """
        cleaned_message = self._clean_message(message)
        response = self._generate_response(cleaned_message)
        return response

    def _clean_message(self, message: str) -> str:
        return message.strip()

    def _generate_response(self, message: str) -> str:
        return f"{self.system_name} received: {message}"


ai_service = AIService()