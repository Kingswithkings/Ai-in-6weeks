from openai import AsyncOpenAI

from app.core.config import settings
from app.db.database import get_connection
from app.services.rag_service import query_documents
from app.services.tools import get_current_time, safe_calculator


class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def process_message(self, message: str) -> str:
        tools = self._detect_tools(message)
        results: list[str] = []

        for tool in tools:
            if tool == "time":
                results.append(f"Time: {get_current_time()}")
            elif tool == "calculator":
                results.append(f"Calculation: {safe_calculator(message)}")

        if results:
            return " | ".join(results)

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

    def _save_to_db(self, user_message: str, ai_response: str) -> None:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO messages (user_message, ai_response) VALUES (?, ?)",
            (user_message, ai_response),
        )
        conn.commit()
        conn.close()

    def _detect_tools(self, message: str) -> list[str]:
        tools: list[str] = []
        lowered = message.lower()

        if "time" in lowered:
            tools.append("time")

        if any(operator in message for operator in ["+", "-", "*", "/"]):
            tools.append("calculator")

        return tools


ai_service = AIService()
