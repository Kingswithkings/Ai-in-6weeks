from typing import Any, TypedDict, cast

from openai import AsyncOpenAI

from app.core.config import settings
from app.db.database import get_connection
from app.services.agent_service import ToolResult, agent_service
from app.services.rag_service import query_documents


ChatMessage = dict[str, str]
HistoryRow = tuple[str, str]


class AIResponse(TypedDict):
    reply: str
    tools_used: list[ToolResult] | None


class AIService:
    """Coordinates tool handling, RAG context, model calls, and chat persistence."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def process_message(self, message: str) -> AIResponse:
        steps = await agent_service.plan(message)

        if steps:
            return self._process_tool_message(steps, message)

        response = await self._generate_response(message)
        self._save_to_db(message, response)

        return {
            "reply": response,
            "tools_used": None,
        }

    def _process_tool_message(self, steps: list[str], message: str) -> AIResponse:
        tool_results = agent_service.execute(steps, message)
        reply = agent_service.format_response(tool_results)

        return {
            "reply": reply,
            "tools_used": tool_results,
        }

    async def _generate_response(self, message: str) -> str:
        history = self._get_recent_history()
        context_text = self._get_context(message)
        messages = self._build_messages(message, history, context_text)

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=cast(Any, messages),
        )

        content = response.choices[0].message.content
        return content.strip() if content else ""

    def _get_recent_history(self) -> list[HistoryRow]:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_message, ai_response FROM messages ORDER BY id DESC LIMIT 5"
            )
            rows = cursor.fetchall()
            return [(user_message, ai_response) for user_message, ai_response in rows]
        finally:
            conn.close()

    def _get_context(self, message: str) -> str:
        context_docs = query_documents(message)
        return "\n".join(context_docs)

    def _build_messages(
        self,
        message: str,
        history: list[HistoryRow],
        context_text: str,
    ) -> list[ChatMessage]:
        messages = [self._system_message(context_text)]

        for user_msg, ai_msg in reversed(history):
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": ai_msg})

        messages.append({"role": "user", "content": message})

        return messages

    def _system_message(self, context_text: str) -> ChatMessage:
        return {
            "role": "system",
            "content": (
                "You are a helpful AI assistant. "
                "Use the provided context to answer the question.\n\n"
                f"Context:\n{context_text}"
            ),
        }

    def _save_to_db(self, user_message: str, ai_response: str) -> None:
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (user_message, ai_response) VALUES (?, ?)",
                (user_message, ai_response),
            )
            conn.commit()
        finally:
            conn.close()


ai_service = AIService()
