import csv
from pathlib import Path


def load_points(path: str | Path = "data/points.csv") -> list[tuple[str, float, float]]:
    points = []

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            point_type = row["type"]
            x = float(row["value1"])
            y = float(row["value2"])
            points.append((point_type, x, y))

    return points

if __name__ == "__main__":
    print(load_points())