"""Date logic only: turn the config into plain objects the templates can read.

No LaTeX in here. Every id is an ISO date such as "2026-08-10" (or "2026-08" for a
month); the templates build link names from them, so both ends of a link always match.
"""
import calendar
import datetime as dt
from dataclasses import dataclass

from .config import Config

ONE_DAY = dt.timedelta(days=1)
ONE_WEEK = dt.timedelta(days=7)


@dataclass(frozen=True)
class Day:
    id: str
    num: int                  # day of the month
    title: str                # "Monday, August 10, 2026"
    month_id: str
    week_id: str              # id of the week page that contains this day
    prev_id: str | None       # None at the edges of the planner
    next_id: str | None


@dataclass(frozen=True)
class WeekDay:
    id: str | None            # None when the day lies outside the planner
    weekday: str              # "Mon"
    num: int


@dataclass(frozen=True)
class Week:
    id: str                   # ISO date of the week's first day
    title: str
    month_id: str             # the month tab this week sits under
    prev_id: str | None
    next_id: str | None
    days: list[WeekDay]


@dataclass(frozen=True)
class Month:
    id: str
    name: str
    title: str                # "August 2026"
    label: str                # "AUG" (tab text)
    weeks: list[list[Day | None]]    # rows of 7; None pads days of other months
    days: list[Day]


@dataclass(frozen=True)
class Planner:
    title: str                # "2026--2027"
    months: list[Month]
    weeks: dict[str, Week]    # by week id
    weekday_names: list[str]  # ["Mon", "Tue", ...] in display order
    weekday_initials: list[str]


def month_id(d: dt.date) -> str:
    return f"{d.year:04d}-{d.month:02d}"


def week_start(d: dt.date, first_weekday: int) -> dt.date:
    """The first day of the week containing d (may lie before the planner starts)."""
    return d - dt.timedelta(days=(d.weekday() - first_weekday) % 7)


def _id_if_in_range(d: dt.date, first: dt.date, last: dt.date) -> str | None:
    return d.isoformat() if first <= d <= last else None


def _make_day(d, first, last, first_weekday) -> Day:
    return Day(
        id=d.isoformat(),
        num=d.day,
        title=f"{d:%A}, {d:%B} {d.day}, {d.year}",      # d.day: no leading zero
        month_id=month_id(d),
        week_id=week_start(d, first_weekday).isoformat(),
        prev_id=_id_if_in_range(d - ONE_DAY, first, last),
        next_id=_id_if_in_range(d + ONE_DAY, first, last),
    )


def _make_month(year, month, first, last, first_weekday) -> Month:
    cal = calendar.Calendar(firstweekday=first_weekday)
    weeks = [[_make_day(d, first, last, first_weekday) if d.month == month else None
              for d in week]
             for week in cal.monthdatescalendar(year, month)]
    return Month(
        id=f"{year:04d}-{month:02d}",
        name=calendar.month_name[month],
        title=f"{calendar.month_name[month]} {year}",
        label=calendar.month_abbr[month].upper(),
        weeks=weeks,
        days=[day for week in weeks for day in week if day],
    )


def _make_week(start, first, last) -> Week:
    days = [start + dt.timedelta(days=i) for i in range(7)]
    end = days[-1]
    if start.year != end.year:
        title = f"{start:%b} {start.day}, {start.year} -- {end:%b} {end.day}, {end.year}"
    else:
        title = f"{start:%b} {start.day} -- {end:%b} {end.day}, {end.year}"
    return Week(
        id=start.isoformat(),
        title=title,
        month_id=month_id(max(start, first)),
        prev_id=(start - ONE_WEEK).isoformat() if start > first else None,
        next_id=(start + ONE_WEEK).isoformat() if start + ONE_WEEK <= last else None,
        days=[WeekDay(id=_id_if_in_range(d, first, last), weekday=f"{d:%a}", num=d.day)
              for d in days],
    )


def _month_range(year, month, count):
    for _ in range(count):
        yield year, month
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def build_planner(cfg: Config) -> Planner:
    ym = list(_month_range(cfg.start_year, cfg.start_month, cfg.months))
    (y0, m0), (y1, m1) = ym[0], ym[-1]
    first = dt.date(y0, m0, 1)
    last = dt.date(y1, m1, calendar.monthrange(y1, m1)[1])

    weeks = {}
    start = week_start(first, cfg.first_weekday)
    while start <= last:
        weeks[start.isoformat()] = _make_week(start, first, last)
        start += ONE_WEEK

    names = [calendar.day_abbr[(cfg.first_weekday + i) % 7] for i in range(7)]
    return Planner(
        title=f"{y0}--{y1}" if y0 != y1 else str(y0),
        months=[_make_month(y, m, first, last, cfg.first_weekday) for y, m in ym],
        weeks=weeks,
        weekday_names=names,
        weekday_initials=[n[0] for n in names],
    )
