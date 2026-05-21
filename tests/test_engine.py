from __future__ import annotations

import matplotlib
import numpy as np
import pytest

from math_tool.engine import SamplingError, sample_function
from math_tool.parser import parse_function
from math_tool.plotter import plot_sampled_function


matplotlib.use("Agg")


def test_sample_linear_function_coordinates() -> None:
    sampled = sample_function(parse_function("y=2x"), x_min=-2, x_max=2, sample_count=5)

    assert len(sampled.segments) == 1
    x_values = sampled.segments[0].x_values
    y_values = sampled.segments[0].y_values
    assert np.allclose(x_values, np.array([-2.0, -1.0, 0.0, 1.0, 2.0]))
    assert np.allclose(y_values, 2 * x_values)


def test_sample_log_function_filters_invalid_domain() -> None:
    sampled = sample_function(parse_function("log(x)"), x_min=-2, x_max=4, sample_count=24)

    assert len(sampled.segments) == 1
    assert np.all(sampled.segments[0].x_values > 0)


def test_sample_reciprocal_function_splits_discontinuity() -> None:
    sampled = sample_function(parse_function("1/x"), x_min=-2, x_max=2, sample_count=40)

    assert len(sampled.segments) == 2
    assert np.all(sampled.segments[0].x_values < 0)
    assert np.all(sampled.segments[1].x_values > 0)


def test_reject_invalid_range() -> None:
    with pytest.raises(SamplingError, match="x_min"):
        sample_function(parse_function("x^2"), x_min=1, x_max=1, sample_count=10)


def test_plot_sampled_function_creates_output_file(tmp_path) -> None:
    sampled = sample_function(
        parse_function("y=x^2+3x-4"),
        x_min=-3,
        x_max=3,
        sample_count=20,
        original_input="y=x^2+3x-4",
    )
    output_path = tmp_path / "curve.png"

    figure, axis = plot_sampled_function(sampled, show_points=True, output_path=output_path, show=False)

    assert output_path.exists()
    assert axis.get_title() == "y=x^2+3x-4"
    figure.clf()