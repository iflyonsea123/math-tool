from __future__ import annotations

import pytest

from math_tool.cli import main


def test_cli_prints_coordinates_without_showing_plot(capsys) -> None:
    exit_code = main(["y=2x", "--x-min", "-1", "--x-max", "1", "--samples", "3", "--coordinate-limit", "3", "--no-show"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Sampled coordinates:" in captured.out
    assert "-1\t-2" in captured.out
    assert "1\t2" in captured.out


def test_cli_supports_latex_input(capsys) -> None:
    exit_code = main([r"y=\frac{1}{x}", "--latex", "--x-min", "-2", "--x-max", "2", "--samples", "10", "--coordinate-limit", "2", "--no-show"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Sampled coordinates:" in captured.out


def test_cli_rejects_invalid_range(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["y=x", "--x-min", "1", "--x-max", "-1", "--no-show"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 2
    assert "x_min must be smaller than x_max" in captured.err