from __future__ import annotations

from pathlib import Path

from matplotlib.axes import Axes
from matplotlib import pyplot as plt

from .engine import SampledFunction


def render_sampled_function(
    axis: Axes,
    sampled: SampledFunction,
    show_points: bool = False,
) -> Axes:
    axis.clear()

    for segment in sampled.segments:
        axis.plot(segment.x_values, segment.y_values, linewidth=2)
        if show_points:
            axis.scatter(segment.x_values, segment.y_values, s=10, alpha=0.7)

    axis.axhline(0, color="black", linewidth=0.8)
    axis.axvline(0, color="black", linewidth=0.8)
    axis.grid(True, linestyle="--", alpha=0.35)
    axis.set_xlabel("x")
    axis.set_ylabel("y")
    axis.set_title(sampled.original_input or f"y = {sampled.expression}")
    return axis


def plot_sampled_function(
    sampled: SampledFunction,
    show_points: bool = False,
    output_path: str | Path | None = None,
    show: bool = True,
):
    figure, axis = plt.subplots(figsize=(9, 6))
    render_sampled_function(axis, sampled, show_points=show_points)

    if output_path is not None:
        figure.savefig(Path(output_path), dpi=150, bbox_inches="tight")

    if show:
        plt.show()

    return figure, axis