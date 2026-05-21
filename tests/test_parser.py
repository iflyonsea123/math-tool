import pytest
from sympy import Rational, log, sin

from math_tool.parser import FunctionParseError, parse_function


def test_parse_linear_expression_with_assignment() -> None:
    expr = parse_function("y=2x")
    assert str(expr) == "2*x"


def test_parse_quadratic_expression() -> None:
    expr = parse_function("y=x^2+3x-4")
    assert str(expr.expand()) == "x**2 + 3*x - 4"


def test_parse_text_function_names() -> None:
    expr = parse_function("sin(x) + log(x)")
    assert expr == sin(parse_function("x")) + log(parse_function("x"))


def test_parse_latex_fraction() -> None:
    expr = parse_function(r"y=\frac{1}{x}", is_latex=True)
    assert expr == 1 / parse_function("x")


def test_parse_double_escaped_latex_fraction() -> None:
    expr = parse_function(r"y=\\frac{1}{x}", is_latex=True)
    assert expr == 1 / parse_function("x")


def test_parse_latex_trig() -> None:
    expr = parse_function(r"\sin\left(x\right)", is_latex=True)
    assert str(expr) == "sin(x)"


def test_reject_multi_variable_expression() -> None:
    with pytest.raises(FunctionParseError, match="Only single-variable"):
        parse_function("y=ax+b")


def test_reject_empty_expression() -> None:
    with pytest.raises(FunctionParseError, match="cannot be empty"):
        parse_function("   ")