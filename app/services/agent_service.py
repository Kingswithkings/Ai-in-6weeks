from app.services.tools import get_current_time, safe_calculator, extract_expression


class AgentService:
    def plan(self, message: str) -> list[str]:
        steps = []
        lower_msg = message.lower()

        if "time" in lower_msg:
            steps.append("time")

        if extract_expression(message):
            steps.append("calculator")

        return steps

    def execute(self, steps: list[str], message: str) -> list[dict]:
        results = []

        for step in steps:
            if step == "time":
                results.append({
                    "tool": "time",
                    "result": get_current_time()
                })

            elif step == "calculator":
                expr = extract_expression(message)
                result = safe_calculator(expr) if expr else "No valid expression found"

                results.append({
                    "tool": "calculator",
                    "result": result
                })

        return results

    def format_response(self, tool_results: list[dict]) -> str:
        if not tool_results:
            return ""

        response_parts = []

        for item in tool_results:
            if item["tool"] == "time":
                response_parts.append(f"Time: {item['result']}")

            elif item["tool"] == "calculator":
                response_parts.append(f"Calculation: {item['result']}")

        return " | ".join(response_parts)


agent_service = AgentService()