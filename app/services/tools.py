import ast
from datetime import datetime
import operator
import re

ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

unary_ops = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def extract_expression(text: str) -> str | None:
    matches = re.findall(r"[\d\.\s\+\-\*\/\(\)]+", text)
    candidates = [
        match.strip()
        for match in matches
        if any(op in match for op in "+-*/") and any(ch.isdigit() for ch in match)
    ]
    return candidates[0] if candidates else None


def safe_calculator(expr: str) -> str:
    try:
        node = ast.parse(expr, mode="eval").body

        def eval_node(node: ast.AST) -> int | float:
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                return node.value
            if isinstance(node, ast.Num):
                return node.n
            if isinstance(node, ast.BinOp) and type(node.op) in ops:
                return ops[type(node.op)](eval_node(node.left), eval_node(node.right))
            if isinstance(node, ast.UnaryOp) and type(node.op) in unary_ops:
                return unary_ops[type(node.op)](eval_node(node.operand))
            raise ValueError("Invalid expression")

        return str(eval_node(node))

    except Exception:
        return "Invalid calculation"
