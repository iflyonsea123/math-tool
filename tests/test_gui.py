from __future__ import annotations

import tkinter as tk

import pytest

from math_tool.gui import MathToolGui, compute_gui_result, format_coordinate_table
from math_tool.parser import parse_function
from math_tool.engine import sample_function, SamplingError


def test_compute_gui_result_for_text_expression() -> None:
    result = compute_gui_result("y=2x", is_latex=False, x_min=-1, x_max=1, sample_count=3, coordinate_limit=3)

    assert result.sampled.original_input == "y=2x"
    assert "Sampled coordinates" in result.coordinate_text
    assert "-1\t-2" in result.coordinate_text


def test_compute_gui_result_for_latex_expression() -> None:
    result = compute_gui_result(r"y=\frac{1}{x}", is_latex=True, x_min=-2, x_max=2, sample_count=10, coordinate_limit=2)

    assert len(result.sampled.segments) == 2
    assert "Sampled coordinates" in result.coordinate_text


def test_format_coordinate_table_rejects_negative_limit() -> None:
    sampled = sample_function(parse_function("x^2"), x_min=-1, x_max=1, sample_count=3)

    with pytest.raises(SamplingError, match="coordinate_limit"):
        format_coordinate_table(sampled, coordinate_limit=-1)


def test_gui_canvas_is_attached_to_plot_frame() -> None:
    root = tk.Tk()
    root.withdraw()

    try:
        app = MathToolGui(root)
        assert app.plot_frame is not None
        assert app.canvas is not None
        assert app.canvas.get_tk_widget().master == app.plot_frame
    finally:
        root.destroy()