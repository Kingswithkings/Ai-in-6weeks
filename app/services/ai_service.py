from openai import AsyncOpenAI

from app.core.config import settings
from app.db.database import get_connection
from app.services.rag_service import query_documents
from app.services.tools import get_current_time, simple_calculator


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def process_message(self, message: str) -> str:
        tool = self._detect_tool(message)

        if tool == "time":
            return get_current_time()

        if tool == "calculator":
            return simple_calculator(message)

        response = await self._generate_response(message)
        self._save_to_db(message, response)
        return response

    async def _generate_response(self, message: str) -> str:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_message, ai_response FROM messages ORDER BY id DESC LIMIT 5"
            )
            history = cursor.fetchall()
        finally:
            conn.close()

        context_docs = query_documents(message)
        context_text = "\n".join(context_docs)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful AI assistant. "
                    "Use the provided context to answer the question.\n\n"
                    f"Context:\n{context_text}"
                ),
            }
        ]

        for user_msg, ai_msg in reversed(history):
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": ai_msg})

        messages.append({"role": "user", "content": message})

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        content = response.choices[0].message.content
        return content.strip() if content else ""

    def _save_to_db(self, user_message: str, ai_response: str):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO messages (user_message, ai_response) VALUES (?, ?)",
            (user_message, ai_response),
        )

        conn.commit()
        conn.close()

    def _detect_tool(self, message: str) -> str | None:
        lowered = message.lower()
        if "time" in lowered:
            return "time"
        if any(operator in message for operator in ["+", "-", "*", "/"]):
            return "calculator"
        return None


ai_service = AIService()
