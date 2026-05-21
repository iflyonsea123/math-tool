from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sympy import Interval, Union, lambdify
from sympy.calculus.util import continuous_domain
from sympy.core.expr import Expr
from sympy.sets.sets import EmptySet

from .parser import X_SYMBOL


class SamplingError(ValueError):
    pass


@dataclass(frozen=True)
class CoordinateSegment:
    x_values: np.ndarray
    y_values: np.ndarray


@dataclass(frozen=True)
class SampledFunction:
    expression: Expr
    x_min: float
    x_max: float
    sample_count: int
    segments: list[CoordinateSegment]
    original_input: str | None = None

    def coordinate_rows(self) -> list[tuple[float, float]]:
        rows: list[tuple[float, float]] = []
        for segment in self.segments:
            rows.extend(zip(segment.x_values.tolist(), segment.y_values.tolist()))
        return rows


def _validate_range(x_min: float, x_max: float, sample_count: int) -> None:
    if x_min >= x_max:
        raise SamplingError("x_min must be smaller than x_max.")
    if sample_count < 2:
        raise SamplingError("sample_count must be at least 2.")


def _extract_intervals(domain_set: object) -> list[Interval]:
    if domain_set == EmptySet:
        return []
    if isinstance(domain_set, Interval):
        return [domain_set]
    if isinstance(domain_set, Union):
        return [item for item in domain_set.args if isinstance(item, Interval)]
    return []


def _interval_length(interval: Interval) -> float:
    return float(interval.end - interval.start)


def _allocate_samples(intervals: list[Interval], sample_count: int) -> list[int]:
    if len(intervals) == 1:
        return [sample_count]

    lengths = np.array([max(_interval_length(interval), 0.0) for interval in intervals], dtype=float)
    if not np.any(lengths):
        return [max(2, sample_count // max(len(intervals), 1)) for _ in intervals]

    raw_counts = np.maximum(2, np.round(sample_count * (lengths / lengths.sum())).astype(int))
    difference = int(sample_count - raw_counts.sum())

    while difference != 0:
        step = 1 if difference > 0 else -1
        for index in np.argsort(-lengths):
            if difference == 0:
                break
            if step < 0 and raw_counts[index] <= 2:
                continue
            raw_counts[index] += step
            difference -= step

    return raw_counts.tolist()


def _sample_interval(function, interval: Interval, sample_count: int) -> CoordinateSegment | None:
    start = float(interval.start)
    end = float(interval.end)
    span = end - start
    if span <= 0:
        return None

    offset = max(span * 1e-6, 1e-9)
    if interval.left_open:
        start += offset
    if interval.right_open:
        end -= offset
    if end <= start:
        return None

    x_values = np.linspace(start, end, sample_count)
    with np.errstate(all="ignore"):
        y_values = function(x_values)

    y_array = np.asarray(y_values)
    real_mask = np.ones_like(x_values, dtype=bool)
    if np.iscomplexobj(y_array):
        real_mask = np.isclose(np.imag(y_array), 0.0, atol=1e-9)
        y_array = np.real(y_array)

    y_array = np.asarray(y_array, dtype=float)
    valid_mask = np.isfinite(x_values) & np.isfinite(y_array) & real_mask
    if not np.any(valid_mask):
        return None

    return CoordinateSegment(x_values=x_values[valid_mask], y_values=y_array[valid_mask])


def sample_function(
    expression: Expr,
    x_min: float = -10.0,
    x_max: float = 10.0,
    sample_count: int = 400,
    original_input: str | None = None,
) -> SampledFunction:
    _validate_range(x_min, x_max, sample_count)

    requested_interval = Interval(x_min, x_max)
    domain = continuous_domain(expression, X_SYMBOL, requested_interval)
    intervals = _extract_intervals(domain)
    if not intervals:
        raise SamplingError("The function has no plottable real values in the requested x range.")

    function = lambdify(X_SYMBOL, expression, modules=["numpy"])
    counts = _allocate_samples(intervals, sample_count)
    segments = [
        segment
        for interval, count in zip(intervals, counts)
        for segment in [_sample_interval(function, interval, count)]
        if segment is not None
    ]
    if not segments:
        raise SamplingError("Unable to sample valid coordinates for the requested function.")

    return SampledFunction(
        expression=expression,
        x_min=x_min,
        x_max=x_max,
        sample_count=sample_count,
        segments=segments,
        original_input=original_input,
    )