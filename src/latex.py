"""Run pdflatex."""
import shutil
import subprocess
from pathlib import Path


def compile_pdf(build_dir: Path, tex_dir: Path, name: str = "planner") -> None:
    """Compile build_dir/<name>.tex. tex_dir holds planner.sty."""
    if shutil.which("pdflatex") is None:
        raise SystemExit("pdflatex not found on PATH (install MiKTeX or TeX Live).")
    # Two passes: the first writes the PDF outline (.out), the second embeds it.
    for _ in range(2):
        result = subprocess.run(
            ["pdflatex", f"-include-directory={tex_dir}",
             "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"],
            cwd=build_dir, capture_output=True, text=True, errors="replace")
        if result.returncode != 0:
            print(result.stdout[-3000:])
            raise SystemExit(f"pdflatex failed; see {build_dir / (name + '.log')}")
