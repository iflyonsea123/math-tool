from __future__ import annotations

import argparse
from collections.abc import Sequence

from .engine import SampledFunction, SamplingError, sample_function
from .parser import FunctionParseError, parse_function
from .plotter import plot_sampled_function


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-tool",
        description="Parse a math function, print sampled coordinates, and plot its curve.",
    )
    parser.add_argument("expression", nargs="?", help="Function expression such as y=2x or y=x^2+3x-4")
    parser.add_argument("--latex", action="store_true", help="Interpret the expression as LaTeX input")
    parser.add_argument("--x-min", type=float, default=-10.0, help="Minimum x value for sampling")
    parser.add_argument("--x-max", type=float, default=10.0, help="Maximum x value for sampling")
    parser.add_argument("--samples", type=int, default=200, help="Number of sample points across the range")
    parser.add_argument(
        "--coordinate-limit",
        type=int,
        default=20,
        help="How many sampled coordinate rows to print before truncating; use 0 for all rows",
    )
    parser.add_argument("--points", action="store_true", help="Overlay sampled points on the plotted curve")
    parser.add_argument("--save", help="Optional output image path, for example output.png")
    parser.add_argument("--no-show", action="store_true", help="Generate the plot without opening a window")
    return parser


def _read_expression(args: argparse.Namespace) -> str:
    if args.expression:
        return args.expression

    expression = input("Enter a function, for example y=2x or y=\\frac{1}{x}: ").strip()
    if not expression:
        raise FunctionParseError("Function input cannot be empty.")
    return expression


def _format_coordinate_table(sampled: SampledFunction, coordinate_limit: int) -> str:
    rows = sampled.coordinate_rows()
    if coordinate_limit < 0:
        raise SamplingError("coordinate_limit must be 0 or greater.")

    shown_rows = rows if coordinate_limit == 0 else rows[:coordinate_limit]
    lines = ["Sampled coordinates:", "x\ty"]
    lines.extend(f"{x_value:.6g}\t{y_value:.6g}" for x_value, y_value in shown_rows)
    if coordinate_limit != 0 and len(rows) > coordinate_limit:
        lines.append(f"... truncated {len(rows) - coordinate_limit} additional points")
    return "\n".join(lines)


def run_cli(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        expression_text = _read_expression(args)
        expression = parse_function(expression_text, is_latex=args.latex)
        sampled = sample_function(
            expression,
            x_min=args.x_min,
            x_max=args.x_max,
            sample_count=args.samples,
            original_input=expression_text,
        )
        print(_format_coordinate_table(sampled, args.coordinate_limit))
        plot_sampled_function(
            sampled,
            show_points=args.points,
            output_path=args.save,
            show=not args.no_show,
        )
    except (FunctionParseError, SamplingError) as exc:
        parser.exit(status=2, message=f"Error: {exc}\n")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    return run_cli(argv)


if __name__ == "__main__":
    raise SystemExit(main())