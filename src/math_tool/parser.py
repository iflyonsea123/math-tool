from __future__ import annotations

import re

from sympy import E, acos, asin, atan, cos, exp, log, pi, sin, sqrt, symbols, tan
from sympy.core.expr import Expr
from sympy.parsing.latex import parse_latex
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)


X_SYMBOL = symbols("x")
TEXT_TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


class FunctionParseError(ValueError):
    pass


def _normalize_latex(expression: str) -> str:
    normalized = expression.strip()
    if normalized.startswith("$") and normalized.endswith("$") and len(normalized) >= 2:
        normalized = normalized[1:-1].strip()
    return re.sub(r"\\{2,}", r"\\", normalized)


def _strip_assignment(expression: str) -> str:
    text = expression.strip()
    if not text:
        raise FunctionParseError("Function input cannot be empty.")

    patterns = [
        r"^y\s*=\s*(.+)$",
        r"^f\s*\(\s*x\s*\)\s*=\s*(.+)$",
    ]
    for pattern in patterns:
        match = re.match(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return text


def _validate_single_variable(expr: Expr) -> Expr:
    invalid_symbols = sorted(
        (symbol for symbol in expr.free_symbols if symbol != X_SYMBOL),
        key=str,
    )
    if invalid_symbols:
        names = ", ".join(str(symbol) for symbol in invalid_symbols)
        raise FunctionParseError(
            f"Only single-variable functions in x are supported. Found: {names}."
        )
    return expr


def parse_function(expression: str, is_latex: bool = False) -> Expr:
    normalized = _strip_assignment(expression)
    if is_latex:
        normalized = _normalize_latex(normalized)

    try:
        if is_latex:
            expr = parse_latex(normalized)
        else:
            expr = parse_expr(
                normalized,
                local_dict={
                    "x": X_SYMBOL,
                    "e": E,
                    "pi": pi,
                    "sin": sin,
                    "cos": cos,
                    "tan": tan,
                    "asin": asin,
                    "acos": acos,
                    "atan": atan,
                    "log": log,
                    "ln": log,
                    "exp": exp,
                    "sqrt": sqrt,
                },
                transformations=TEXT_TRANSFORMATIONS,
                evaluate=True,
            )
    except Exception as exc:  # pragma: no cover - sympy raises multiple exception types
        kind = "LaTeX" if is_latex else "text"
        raise FunctionParseError(f"Unable to parse {kind} function input: {expression}") from exc

    return _validate_single_variable(expr)