import ast
import operator
import os
from typing import Any, Dict

from app.rag import PrivateRAG
from app.ml import TinyMLClassifier

_ALLOWED_AST_NODES = {
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow, ast.Mod,
    ast.USub, ast.UAdd, ast.Load,
}

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def _safe_eval_expr(expr: str) -> float:
    tree = ast.parse(expr, mode="eval")
    for node in ast.walk(tree):
        if type(node) not in _ALLOWED_AST_NODES:
            raise ValueError(f"Disallowed expression element: {type(node).__name__}")

    def _eval(node: ast.AST) -> Any:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):
                raise ValueError("Only numeric constants are allowed")
            return node.value
        if isinstance(node, ast.Num):
            return node.n
        if isinstance(node, ast.BinOp):
            op = _OPERATORS[type(node.op)]
            return op(_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp):
            op = _OPERATORS[type(node.op)]
            return op(_eval(node.operand))
        raise ValueError("Unsupported expression")

    return _eval(tree)

class LocalAgentRuntime:
    def __init__(self, rag: PrivateRAG, classifier: TinyMLClassifier):
        self.rag = rag
        self.classifier = classifier
        approved = os.getenv("APPROVED_TOOLS", "calculator,document_search,ticket_classifier")
        self.approved_tools = {x.strip() for x in approved.split(",") if x.strip()}

    def run(self, tool: str, tool_input: str) -> Dict[str, Any]:
        if tool not in self.approved_tools:
            return {
                "allowed": False,
                "tool": tool,
                "error": f"Tool '{tool}' is not approved. Approved tools: {sorted(self.approved_tools)}",
            }

        if tool == "calculator":
            result = _safe_eval_expr(tool_input)
            return {"allowed": True, "tool": tool, "result": result, "policy": "local-arithmetic-only"}

        if tool == "document_search":
            result = self.rag.answer(tool_input)
            return {"allowed": True, "tool": tool, "result": result, "policy": "approved-internal-documents-only"}

        if tool == "ticket_classifier":
            result = self.classifier.classify(tool_input)
            return {"allowed": True, "tool": tool, "result": result, "policy": "approved-local-ml-model-only"}

        return {"allowed": False, "tool": tool, "error": "Tool is configured but not implemented."}
