#!/usr/bin/env python3
"""Friendly CI checker for the project-structure exercise.

This checker intentionally uses only the Python standard library. It is not a
unit-test suite; it checks whether the repository has become a reproducible,
structured Python project.
"""

import os
import subprocess
import sys
import tomllib

results = []


def add_result(label, ok, detail=""):
    results.append((label, bool(ok), detail))


def run(command):
    return subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def exists(path):
    return os.path.isfile(path)


required_files = [
    "pyproject.toml",
    "uv.lock",
    ".gitignore",
    os.path.join("src", "ascii_plotter", "__init__.py"),
    os.path.join("src", "ascii_plotter", "io.py"),
    os.path.join("src", "ascii_plotter", "plot.py"),
    os.path.join("src", "ascii_plotter", "cli.py"),
]

for path in required_files:
    add_result(f"{path} exists", exists(path))

# .gitignore
if exists(".gitignore"):
    with open(".gitignore", encoding="utf-8") as file:
        ignore_text = file.read()
    add_result(".venv is listed in .gitignore", ".venv" in ignore_text)

    check_ignore = run(["git", "check-ignore", "-q", ".venv/placeholder.txt"])
    add_result("Git really ignores .venv/", check_ignore.returncode == 0)
else:
    add_result(".venv is listed in .gitignore", False)
    add_result("Git really ignores .venv/", False)

tracked = run(["git", "ls-files", ".venv"])
tracked_env = [line for line in tracked.stdout.splitlines() if line.strip()]
add_result(
    ".venv contains no tracked files",
    not tracked_env,
    "Tracked: " + ", ".join(tracked_env[:3]) if tracked_env else "",
)

# pyproject.toml
project_ok = False
if exists("pyproject.toml"):
    try:
        with open("pyproject.toml", "rb") as file:
            config = tomllib.load(file)
        project = config.get("project", {})
        dependencies = project.get("dependencies", [])
        rich_declared = any(
            isinstance(dep, str) and dep.strip().lower().startswith("rich")
            for dep in dependencies
        )
        add_result("project name is ascii-plotter", project.get("name") == "ascii-plotter")
        add_result("rich is declared as dependency", rich_declared)
        add_result("a build-system is configured", bool(config.get("build-system")))
        project_ok = True
    except Exception as error:
        add_result("pyproject.toml can be parsed", False, str(error))
else:
    add_result("project name is ascii-plotter", False)
    add_result("rich is declared as dependency", False)
    add_result("a build-system is configured", False)

# Two contributors after the prepared starter state.
tag_check = run(["git", "rev-parse", "--verify", "refs/tags/starter"])
if tag_check.returncode == 0:
    history = run(["git", "log", "starter..HEAD", "--format=%ae"])
    authors = sorted({line.strip() for line in history.stdout.splitlines() if line.strip()})
    add_result(
        "commits from at least two contributors",
        len(authors) >= 2,
        f"Found {len(authors)} unique commit email(s)",
    )
else:
    add_result(
        "commits from at least two contributors",
        False,
        "starter tag not found",
    )

# Reproducibility and runnable package. Only attempt these if the basic project
# metadata exists; otherwise produce useful SKIP-style failures instead of a
# wall of subprocess tracebacks.
if project_ok and exists("uv.lock"):
    sync = run(["uv", "sync", "--locked"])
    add_result("uv sync --locked succeeds", sync.returncode == 0, sync.stdout[-500:])

    if sync.returncode == 0:
        package_import = run(["uv", "run", "python", "-c", "import ascii_plotter"])
        add_result(
            "ascii_plotter can be imported",
            package_import.returncode == 0,
            package_import.stdout[-500:],
        )

        cli = run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "ascii_plotter.cli",
                os.path.join("data", "points.csv"),
            ]
        )
        add_result(
            "CLI processes data/points.csv",
            cli.returncode == 0,
            cli.stdout[-500:],
        )
    else:
        add_result("ascii_plotter can be imported", False, "uv sync failed first")
        add_result("CLI processes data/points.csv", False, "uv sync failed first")
else:
    add_result("uv sync --locked succeeds", False, "pyproject.toml or uv.lock missing")
    add_result("ascii_plotter can be imported", False, "project not ready")
    add_result("CLI processes data/points.csv", False, "project not ready")

print("\nPROJECT STRUCTURE CHECK")
print("=" * 72)

for label, ok, detail in results:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label}")
    if detail and not ok:
        for line in detail.strip().splitlines()[-5:]:
            print(f"       {line}")

passed = sum(ok for _, ok, _ in results)
print("-" * 72)
print(f"Result: {passed}/{len(results)} checks passed")

if passed != len(results):
    print("\nRead the FAIL lines, fix one issue at a time, commit, and push again.")
    sys.exit(1)

print("\nAll project-structure checks passed.")
