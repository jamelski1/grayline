"""Date utility functions for Grayline."""

import pandas as pd


def generate_week_starts(start: str, periods: int = 104) -> list[pd.Timestamp]:
    """Generate a list of Monday-aligned week start dates."""
    return list(pd.date_range(start=start, periods=periods, freq="W-MON"))


def current_week_start() -> pd.Timestamp:
    """Return the most recent Monday."""
    today = pd.Timestamp.now().normalize()
    return today - pd.Timedelta(days=today.weekday())


def date_to_week_start(dt: pd.Timestamp) -> pd.Timestamp:
    """Snap a date to its enclosing Monday-start week."""
    return dt - pd.Timedelta(days=dt.weekday())
