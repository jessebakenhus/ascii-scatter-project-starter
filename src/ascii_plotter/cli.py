import os
import sys

from .io import load_points
from .plot import render_scatter


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m ascii_plotter.cli <csv-file>")
        raise SystemExit(1)

    csv_path = os.path.abspath(sys.argv[1])

    if not os.path.isfile(csv_path):
        print(f"File not found: {csv_path}")
        raise SystemExit(1)

    points = load_points(csv_path)
    render_scatter(points)


if __name__ == "__main__":
    main()