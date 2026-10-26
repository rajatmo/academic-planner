# Planner

Python works out the data, Jinja templates hold the page structure, LaTeX typesets it.

```
python build.py              # full planner -> build/planner.pdf
python build.py --only day   # one sample page (year|month|week|day|journal), compiles in ~1 s
python build.py --no-pdf     # only write build/planner.tex
```

Needs Python 3.11+, `pip install jinja2`, and `pdflatex` on PATH.

```
config.toml                  paper size, margins (% of page), first month, week start, hours, rows
build.py                     entry point: config -> data -> render -> compile
src/
  config.py                  read config.toml into a typed Config
  calendar_data.py           date logic: Day, Week, Month, Planner (no LaTeX)
  render.py                  Jinja setup and the template syntax
  pages.py                   which pages exist, in what order, which template draws each
  latex.py                   run pdflatex
templates/
  document.tex.j2            paper, margins, tab strip, then the pages
  pages/  year  month  week  day  journal  (.tex.j2)   one page layout each
tex/
  planner.sty                reusable boxes: tab strip, header, rows, grid cells
build/                       generated output
```

## How a page is made

1. `calendar_data.py` turns the config into objects, e.g. a `Day` with `id="2026-08-10"`,
   `prev_id`, `next_id`, `week_id`.
2. `pages.py` yields `("day", {"day": <Day>})` and so on, in page order.
3. `templates/pages/day.tex.j2` is filled with that data and loops over hours, rows, links.
4. The pages are pasted into `document.tex.j2`, written to `build/planner.tex`, compiled.

## Links

Every link name is built from an id: `day-2026-08-10`, `week-2026-08-10`, `month-2026-08`,
`journal-2026-08-10`, `year`. A template writes `\hyperlink{day-<id>}{...}` and the day
template writes the matching `\hypertarget{day-<id>}`, so both ends always agree.

## Template syntax

| Write                                | Meaning                                     |
| ------------------------------------ | ------------------------------------------- |
| `\VAR{ day.title }`                  | insert a value                              |
| `%% for day in week` ... `%% endfor` | a line of logic (also a valid TeX comment)  |
| `%# note`                            | a template comment, removed from the output |

Inside `\hbox{...}` and `\parbox{...}` a line break becomes a space, so lines emitted
there end with `%`.

## Adding a page type

1. `templates/pages/<kind>.tex.j2`, starting with `\BeginPage{...}` and `\PageHeader{...}`.
2. Add `<kind>` to `PAGE_KINDS` and a `yield` in `page_sequence` (`src/pages.py`).
3. If it needs new data, add a field in `src/calendar_data.py`.


