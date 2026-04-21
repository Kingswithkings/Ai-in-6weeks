import ast
from datetime import datetime
import operator

ops = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def get_current_time() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def safe_calculator(expr: str) -> str:
    try:
        node = ast.parse(expr, mode="eval").body

        def eval_node(n):
            if isinstance(n, ast.Num):
                return n.n
            if isinstance(n, ast.BinOp):
                return ops[type(n.op)](eval_node(n.left), eval_node(n.right))
            raise ValueError("Invalid expression")

        return str(eval_node(node))

    except Exception:
        return "Invalid calculation"
