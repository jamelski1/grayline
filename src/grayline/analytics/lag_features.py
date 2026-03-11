"""Lagged variable generation for lead/lag analysis."""

import pandas as pd

from grayline.config.settings import settings


def add_lag_features(
    df: pd.DataFrame,
    columns: list[str],
    lags: list[int] | None = None,
) -> pd.DataFrame:
    """Add lagged versions of specified columns.

    Args:
        df: DataFrame sorted by week_start.
        columns: Column names to create lags for.
        lags: List of lag periods in weeks. Defaults to settings.default_lag_weeks.

    Returns:
        DataFrame with new columns named '{col}_lag_{n}w'.
    """
    if lags is None:
        lags = settings.default_lag_weeks

    df = df.copy().sort_values("week_start")
    for col in columns:
        if col in df.columns:
            for n in lags:
                df[f"{col}_lag_{n}w"] = df[col].shift(n)
    return df
