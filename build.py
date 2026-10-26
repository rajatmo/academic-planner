#!/usr/bin/env python3
"""Build the planner:  config.toml -> data -> Jinja templates -> .tex -> PDF.

    python build.py                 full planner -> build/planner.pdf
    python build.py --only day      one sample page of that kind, for quick layout tests
    python build.py --no-pdf        only write build/planner.tex
"""
import argparse
from pathlib import Path

from src.calendar_data import build_planner
from src.config import load_config
from src.latex import compile_pdf
from src.pages import PAGE_KINDS, render_document

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the planner PDF.")
    parser.add_argument("--only", choices=PAGE_KINDS, help="render a single sample page")
    parser.add_argument("--no-pdf", action="store_true", help="write the .tex but do not compile")
    args = parser.parse_args()

    cfg = load_config(HERE / "config.toml")
    planner = build_planner(cfg)
    tex = render_document(cfg, planner, HERE / "templates", only=args.only)

    BUILD.mkdir(exist_ok=True)
    (BUILD / "planner.tex").write_text(tex, encoding="utf-8")
    print("wrote build/planner.tex")
    if not args.no_pdf:
        compile_pdf(BUILD, HERE / "tex")
        print("wrote build/planner.pdf")


if __name__ == "__main__":
    main()
