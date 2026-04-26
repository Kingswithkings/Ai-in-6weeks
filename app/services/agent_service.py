import json
import re
from typing import Any, TypedDict, cast

from openai import AsyncOpenAI

from app.core.config import settings
from app.services.tools import extract_expression, get_current_time, safe_calculator


ALLOWED_TOOLS: set[str] = {"time", "calculator"}
ChatMessage = dict[str, str]

PLANNER_PROMPT = """
You are an AI planner.

Decide which tools are needed to answer the user.

Available tools:
- time: get current time
- calculator: solve math expressions

Return ONLY valid JSON:
{"tools": ["tool1", "tool2"]}

If no tools needed:
{"tools": []}
"""

REFLECTION_PROMPT = """
You are an AI assistant.

Use ONLY the provided tool results to answer.
Do not invent facts.
Keep the answer concise.
"""


class ToolResult(TypedDict):
    tool: str
    result: str


class AgentService:
    """Plans tool usage, runs tools, and formats tool-based answers."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL

    async def plan(self, message: str) -> list[str]:
        fallback_steps = self._fallback_plan(message)
        if fallback_steps:
            return fallback_steps

        try:
            content = await self._ask_planner(message)
            return self._parse_plan(content)
        except Exception:
            return fallback_steps

    async def _ask_planner(self, message: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=cast(Any, self._build_messages(PLANNER_PROMPT, message)),
            temperature=0,
        )

        return response.choices[0].message.content or ""

    def _parse_plan(self, content: str) -> list[str]:
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if not json_match:
            return []

        try:
            data: Any = json.loads(json_match.group())
        except json.JSONDecodeError:
            return []

        if not isinstance(data, dict):
            return []

        tools = data.get("tools", [])
        if not isinstance(tools, list):
            return []

        return [
            tool
            for tool in tools
            if isinstance(tool, str) and tool in ALLOWED_TOOLS
        ]

    def _fallback_plan(self, message: str) -> list[str]:
        steps: list[str] = []
        lower_message = message.lower()

        if "time" in lower_message:
            steps.append("time")

        if extract_expression(message):
            steps.append("calculator")

        return steps

    def execute(self, steps: list[str], message: str) -> list[ToolResult]:
        results: list[ToolResult] = []

        for step in steps:
            if step == "time":
                results.append(self._run_time_tool())
            elif step == "calculator":
                results.append(self._run_calculator_tool(message))

        return results

    def _run_time_tool(self) -> ToolResult:
        return {
            "tool": "time",
            "result": get_current_time(),
        }

    def _run_calculator_tool(self, message: str) -> ToolResult:
        expression = extract_expression(message)
        result = safe_calculator(expression) if expression else "No valid expression found"

        return {
            "tool": "calculator",
            "result": result,
        }

    async def reflect_and_answer(
        self,
        message: str,
        tool_results: list[ToolResult],
    ) -> str:
        if not tool_results:
            return ""

        user_content = (
            f"User message: {message}\n\n"
            f"Tool results: {tool_results}"
        )

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=cast(
                    Any,
                    self._build_messages(REFLECTION_PROMPT, user_content),
                ),
                temperature=0,
            )
        except Exception:
            return self.format_response(tool_results)

        content = response.choices[0].message.content
        return content.strip() if content else self.format_response(tool_results)

    def _build_messages(self, system_prompt: str, user_content: str) -> list[ChatMessage]:
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ]

    def format_response(self, tool_results: list[ToolResult]) -> str:
        response_parts: list[str] = []

        for item in tool_results:
            if item["tool"] == "time":
                response_parts.append(f"Time: {item['result']}")
            elif item["tool"] == "calculator":
                response_parts.append(f"Calculation: {item['result']}")

        return " | ".join(response_parts)


agent_service = AgentService()
