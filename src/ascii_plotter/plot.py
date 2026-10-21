from rich.console import Console
from rich.text import Text

STYLES = {
    "A": "bold cyan",
    "B": "bold magenta",
    "C": "bold green",
    "D": "bold yellow",
    "*": "bold red",   # Kollision: mehrere Punkte auf derselben Stelle
}

console = Console()


def scale(value, minimum, maximum, size):
    if maximum == minimum:
        return 0
    relative = (value - minimum) / (maximum - minimum)
    return round(relative * (size - 1))


def render_scatter(points, width=40, height=15):
    if not points:
        console.print("Keine Daten.")
        return

    xs = [x for _, x, _ in points]
    ys = [y for _, _, y in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    # leeres Raster
    grid = [[" " for _ in range(width)] for _ in range(height)]

    for name, x, y in points:
        x_pos = scale(x, min_x, max_x, width)
        y_pos = scale(y, min_y, max_y, height)
        row = height - 1 - y_pos          # y umdrehen: oben = großer Wert

        if grid[row][x_pos] == " ":
            grid[row][x_pos] = name
        else:
            grid[row][x_pos] = "*"        # zwei Punkte auf einer Stelle

    # ausgeben, Zeile für Zeile
    for i, row in enumerate(grid):
        line = Text()

        # y-Beschriftung links: oben Maximum, unten Minimum
        if i == 0:
            label = f"{max_y:>5.1f} |"
        elif i == height - 1:
            label = f"{min_y:>5.1f} |"
        else:
            label = "      |"
        line.append(label)

        for symbol in row:
            if symbol in STYLES:
                line.append(symbol, style=STYLES[symbol])
            else:
                line.append(symbol)

        console.print(line)

    # x-Achse
    console.print("      +" + "-" * width)
    console.print(f"       {min_x:<.1f}" + " " * (width - 8) + f"{max_x:>.1f}")


if __name__ == "__main__":
    points = [
        ("A", 1.2, 7.8),
        ("B", 2.7, 5.1),
        ("C", 4.8, 8.4),
        ("D", 8.2, 2.0),
    ]
    render_scatter(points)