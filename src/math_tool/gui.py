from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .engine import SampledFunction, SamplingError, sample_function
from .parser import FunctionParseError, parse_function
from .plotter import render_sampled_function


@dataclass(frozen=True)
class GuiComputationResult:
    sampled: SampledFunction
    coordinate_text: str


def format_coordinate_table(sampled: SampledFunction, coordinate_limit: int = 50) -> str:
    rows = sampled.coordinate_rows()
    if coordinate_limit < 0:
        raise SamplingError("coordinate_limit must be 0 or greater.")

    shown_rows = rows if coordinate_limit == 0 else rows[:coordinate_limit]
    lines = ["Sampled coordinates", "x\ty"]
    lines.extend(f"{x_value:.6g}\t{y_value:.6g}" for x_value, y_value in shown_rows)
    if coordinate_limit != 0 and len(rows) > coordinate_limit:
        lines.append(f"... truncated {len(rows) - coordinate_limit} additional points")
    return "\n".join(lines)


def compute_gui_result(
    expression_text: str,
    *,
    is_latex: bool,
    x_min: float,
    x_max: float,
    sample_count: int,
    coordinate_limit: int = 50,
) -> GuiComputationResult:
    expression = parse_function(expression_text, is_latex=is_latex)
    sampled = sample_function(
        expression,
        x_min=x_min,
        x_max=x_max,
        sample_count=sample_count,
        original_input=expression_text,
    )
    return GuiComputationResult(
        sampled=sampled,
        coordinate_text=format_coordinate_table(sampled, coordinate_limit=coordinate_limit),
    )


class MathToolGui:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Math Tool")
        self.root.geometry("1200x760")

        self.expression_var = tk.StringVar(value="y=x^2+3x-4")
        self.latex_var = tk.BooleanVar(value=False)
        self.points_var = tk.BooleanVar(value=False)
        self.x_min_var = tk.StringVar(value="-10")
        self.x_max_var = tk.StringVar(value="10")
        self.samples_var = tk.StringVar(value="200")
        self.status_var = tk.StringVar(value="Ready")
        self.current_result: GuiComputationResult | None = None

        self.figure = Figure(figsize=(7, 5), dpi=100)
        self.axis = self.figure.add_subplot(111)
        self.plot_frame: ttk.Frame | None = None
        self.canvas: FigureCanvasTkAgg | None = None

        self.coordinate_text = tk.Text(self.root, width=36, height=20, wrap="none")
        self.coordinate_text.configure(state="disabled")

        self._build_layout()
        self._render_placeholder()

    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        control_frame = ttk.Frame(self.root, padding=16)
        control_frame.grid(row=0, column=0, sticky="ns")
        self.plot_frame = ttk.Frame(self.root, padding=(0, 16, 16, 16))
        self.plot_frame.grid(row=0, column=1, sticky="nsew")
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.rowconfigure(0, weight=1)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.plot_frame)

        ttk.Label(control_frame, text="Function input").grid(row=0, column=0, sticky="w")
        expression_entry = ttk.Entry(control_frame, textvariable=self.expression_var, width=34)
        expression_entry.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 10))
        expression_entry.focus_set()

        ttk.Checkbutton(control_frame, text="Interpret as LaTeX", variable=self.latex_var).grid(
            row=2, column=0, columnspan=2, sticky="w"
        )
        ttk.Checkbutton(control_frame, text="Show sample points", variable=self.points_var).grid(
            row=3, column=0, columnspan=2, sticky="w", pady=(0, 12)
        )

        ttk.Label(control_frame, text="x min").grid(row=4, column=0, sticky="w")
        ttk.Label(control_frame, text="x max").grid(row=4, column=1, sticky="w")
        ttk.Entry(control_frame, textvariable=self.x_min_var, width=12).grid(row=5, column=0, sticky="ew", padx=(0, 8))
        ttk.Entry(control_frame, textvariable=self.x_max_var, width=12).grid(row=5, column=1, sticky="ew")

        ttk.Label(control_frame, text="Samples").grid(row=6, column=0, sticky="w", pady=(12, 0))
        ttk.Entry(control_frame, textvariable=self.samples_var, width=12).grid(row=7, column=0, sticky="ew", pady=(4, 12))

        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(0, 12))
        ttk.Button(button_frame, text="Plot", command=self.plot_expression).grid(row=0, column=0, padx=(0, 8))
        ttk.Button(button_frame, text="Save Image", command=self.save_plot).grid(row=0, column=1, padx=(0, 8))
        ttk.Button(button_frame, text="Clear", command=self.clear_output).grid(row=0, column=2)

        ttk.Label(control_frame, text="Coordinates").grid(row=9, column=0, columnspan=2, sticky="w")
        coordinate_frame = ttk.Frame(control_frame)
        coordinate_frame.grid(row=10, column=0, columnspan=2, sticky="nsew", pady=(4, 0))
        coordinate_scroll = ttk.Scrollbar(coordinate_frame, orient="vertical", command=self.coordinate_text.yview)
        self.coordinate_text.configure(yscrollcommand=coordinate_scroll.set)
        self.coordinate_text.grid(row=0, column=0, sticky="nsew")
        coordinate_scroll.grid(row=0, column=1, sticky="ns")
        coordinate_frame.rowconfigure(0, weight=1)
        coordinate_frame.columnconfigure(0, weight=1)
        control_frame.rowconfigure(10, weight=1)

        status_label = ttk.Label(control_frame, textvariable=self.status_var, foreground="#1f4d3d")
        status_label.grid(row=11, column=0, columnspan=2, sticky="w", pady=(12, 0))

        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, sticky="nsew")

    def _render_placeholder(self) -> None:
        self.axis.clear()
        self.axis.text(0.5, 0.5, "Enter a function and click Plot", ha="center", va="center", fontsize=14)
        self.axis.set_axis_off()
        self.canvas.draw_idle()

    def _set_coordinate_text(self, value: str) -> None:
        self.coordinate_text.configure(state="normal")
        self.coordinate_text.delete("1.0", tk.END)
        self.coordinate_text.insert("1.0", value)
        self.coordinate_text.configure(state="disabled")

    def _read_numeric_inputs(self) -> tuple[float, float, int]:
        try:
            x_min = float(self.x_min_var.get().strip())
            x_max = float(self.x_max_var.get().strip())
            sample_count = int(self.samples_var.get().strip())
        except ValueError as exc:
            raise SamplingError("x range and sample count must be numeric values.") from exc
        return x_min, x_max, sample_count

    def plot_expression(self) -> None:
        expression_text = self.expression_var.get().strip()

        try:
            x_min, x_max, sample_count = self._read_numeric_inputs()
            result = compute_gui_result(
                expression_text,
                is_latex=self.latex_var.get(),
                x_min=x_min,
                x_max=x_max,
                sample_count=sample_count,
            )
        except (FunctionParseError, SamplingError) as exc:
            self.status_var.set(f"Error: {exc}")
            messagebox.showerror("Math Tool", str(exc), parent=self.root)
            return

        self.current_result = result
        self.axis.set_axis_on()
        render_sampled_function(self.axis, result.sampled, show_points=self.points_var.get())
        self.canvas.draw_idle()
        self._set_coordinate_text(result.coordinate_text)
        self.status_var.set("Plot updated")

    def save_plot(self) -> None:
        if self.current_result is None:
            messagebox.showinfo("Math Tool", "Plot a function before saving an image.", parent=self.root)
            return

        output_path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save plot image",
            defaultextension=".png",
            filetypes=[("PNG image", "*.png"), ("JPEG image", "*.jpg"), ("All files", "*.*")],
        )
        if not output_path:
            return

        self.figure.savefig(Path(output_path), dpi=150, bbox_inches="tight")
        self.status_var.set(f"Saved image to {output_path}")

    def clear_output(self) -> None:
        self.current_result = None
        self._set_coordinate_text("")
        self.status_var.set("Ready")
        self._render_placeholder()


def main() -> int:
    root = tk.Tk()
    MathToolGui(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())