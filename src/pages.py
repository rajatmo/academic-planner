"""Which pages exist, in what order, and which template draws each one."""
from collections.abc import Iterator
from pathlib import Path

from .calendar_data import Planner
from .config import Config
from .render import Renderer

PAGE_KINDS = ("year", "month", "week", "day", "journal")


def page_sequence(planner: Planner) -> Iterator[tuple[str, dict]]:
    """Yield (kind, template data) in page order.

    year, then for each month: its month page, and in date order a week page
    before the first day of each week, then each day page followed by its journal.
    """
    yield "year", {}
    seen_weeks = set()
    for month in planner.months:
        yield "month", {"month": month}
        for day in month.days:
            if day.week_id not in seen_weeks:
                seen_weeks.add(day.week_id)
                yield "week", {"week": planner.weeks[day.week_id]}
            yield "day", {"day": day}
            yield "journal", {"day": day}


def hour_labels(first: int, last: int) -> list[str]:
    """05 ... 12 01 ... 10: 12-hour labels, as in the reference planner."""
    return [f"{h % 12 or 12:02d}" for h in range(first, last + 1)]


def render_document(cfg: Config, planner: Planner, templates_dir: Path,
                    only: str | None = None) -> str:
    """The full .tex text. `only` keeps just the first page of one kind (for quick tests)."""
    renderer = Renderer(templates_dir, cfg=cfg, planner=planner,
                        hours=hour_labels(cfg.schedule_start, cfg.schedule_end))
    pages = list(page_sequence(planner))
    if only:
        pages = [next(page for page in pages if page[0] == only)]
    body = "\n".join(renderer.render(f"pages/{kind}.tex.j2", **data) for kind, data in pages)
    return renderer.render("document.tex.j2", body=body)
