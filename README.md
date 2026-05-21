# Math Tool

`math-tool` is a local Python command-line utility for parsing a function, printing sampled coordinates, and plotting the corresponding curve. It supports both plain text input and LaTeX input for single-variable functions in `x`.

## Features

- Parse text expressions such as `y=2x`, `y=x^2+3x-4`, `sin(x)`, `log(x)`, and `1/x`
- Parse LaTeX expressions such as `y=\frac{1}{x}` and `\sin\left(x\right)`
- Print sampled coordinate rows directly in the terminal
- Plot continuous segments separately to avoid drawing across discontinuities like `1/x`
- Accept a default x range or a custom range from the command line

## Install

```bash
python -m pip install -e ".[dev]"
```

## Usage

### Desktop GUI

```bash
python -m math_tool.gui
```

Or, after editable install:

```bash
math-tool-gui
```

The GUI lets you enter a function, choose whether it is LaTeX, set the x range and sample count, inspect sampled coordinates, and save the current plot image.

### Plain text input

```bash
python -m math_tool.cli "y=2x" --x-min -5 --x-max 5 --samples 11
python -m math_tool.cli "y=x^2+3x-4" --save quadratic.png
python -m math_tool.cli "sin(x)" --points
python -m math_tool.cli "log(x,3)" --save log.png
```

### LaTeX input

```bash
python -m math_tool.cli "y=\frac{1}{x}" --latex --x-min -5 --x-max 5
python -m math_tool.cli "\sin\left(x\right)" --latex
```

In PowerShell, a single backslash is the normal way to type LaTeX commands. The parser also accepts doubled backslashes from older examples, but `\frac` is no longer required.

### Interactive mode

```bash
python -m math_tool.cli
```

If no expression is provided, the program prompts for one.

## Common options

- `--latex`: treat the input as LaTeX
- `--x-min` and `--x-max`: set the sampling range
- `--samples`: set the total number of sample points
- `--coordinate-limit`: set how many coordinate rows to print; `0` prints all rows
- `--points`: overlay sampled points on the plotted curve
- `--save output.png`: save the plot image to a file
- `--no-show`: build the plot without opening a window

## Current scope

- Supported: single-variable explicit functions `y=f(x)`
- Not yet supported: implicit functions, parametric equations, multi-variable functions

The desktop GUI is available, but the math engine scope remains the same: single-variable explicit functions only.

## Notes on LaTeX support

SymPy's LaTeX parser requires `antlr4-python3-runtime` version `4.11.x`. The project pins that dependency automatically in `pyproject.toml`.