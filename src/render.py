"""Jinja setup. This file defines the template syntax; nothing else knows about it.

Jinja's defaults ({{ }}, {% %}, {# #}) clash with TeX braces, so templates use:

    \\VAR{ x }              insert a value
    %% for ... / %% if ...  a line of template logic (also a valid TeX comment)
    %# note                 a template comment, removed from the output

Rule for templates: inside \\hbox{...} and \\parbox{...} a line break becomes a space,
so lines emitted there end with a TeX "%".
"""
from pathlib import Path

import jinja2


def _frac(percent: float) -> str:
    """4 -> '0.04': the factor TeX multiplies by a length, e.g. 0.04\\paperwidth."""
    return f"{percent / 100:g}"


class Renderer:
    def __init__(self, templates_dir: Path, **context):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(templates_dir),
            variable_start_string=r"\VAR{", variable_end_string="}",
            block_start_string=r"\BLOCK{", block_end_string="}",      # unused; avoids "{%"
            comment_start_string=r"\#{", comment_end_string="}",      # unused; avoids "{#"
            line_statement_prefix="%%",
            line_comment_prefix="%#",
            keep_trailing_newline=True,
            undefined=jinja2.StrictUndefined,       # a typo in a template is an error
        )
        self.env.filters["frac"] = _frac
        self.env.globals.update(context)            # visible in every template

    def render(self, template_name: str, **context) -> str:
        return self.env.get_template(template_name).render(**context)
