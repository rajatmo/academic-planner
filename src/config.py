"""Settings: read config.toml into one typed, validated object."""
import tomllib
from dataclasses import dataclass
from pathlib import Path

WEEK_STARTS = {"monday": 0, "sunday": 6}      # values match datetime.weekday()


@dataclass(frozen=True)
class Config:
    # paper
    width_mm: float
    height_mm: float
    # layout (percentages of the page)
    margin_left_pct: float
    margin_top_pct: float
    margin_bottom_pct: float
    tab_width_pct: float
    tab_gap_pct: float
    # calendar
    start_year: int
    start_month: int
    months: int
    first_weekday: int
    # day page
    schedule_start: int
    schedule_end: int
    task_rows: int
    # journal page
    journal_lines: int


def load_config(path: Path) -> Config:
    with open(path, "rb") as f:
        raw = tomllib.load(f)

    year, month = map(int, raw["calendar"]["start"].split("-"))
    week_start = raw["calendar"]["week_start"].lower()
    if week_start not in WEEK_STARTS:
        raise ValueError(f"week_start must be one of {sorted(WEEK_STARTS)}, got {week_start!r}")
    if not 0 <= raw["day"]["schedule_start"] <= raw["day"]["schedule_end"] <= 23:
        raise ValueError("schedule_start and schedule_end must satisfy 0 <= start <= end <= 23")

    return Config(
        width_mm=raw["paper"]["width_mm"],
        height_mm=raw["paper"]["height_mm"],
        margin_left_pct=raw["layout"]["margin_left_pct"],
        margin_top_pct=raw["layout"]["margin_top_pct"],
        margin_bottom_pct=raw["layout"]["margin_bottom_pct"],
        tab_width_pct=raw["layout"]["tab_width_pct"],
        tab_gap_pct=raw["layout"]["tab_gap_pct"],
        start_year=year,
        start_month=month,
        months=raw["calendar"]["months"],
        first_weekday=WEEK_STARTS[week_start],
        schedule_start=raw["day"]["schedule_start"],
        schedule_end=raw["day"]["schedule_end"],
        task_rows=raw["day"]["task_rows"],
        journal_lines=raw["journal"]["lines"],
    )
