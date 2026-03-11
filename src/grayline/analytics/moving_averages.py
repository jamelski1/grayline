"""Moving average calculations for indicator smoothing."""

import pandas as pd


def add_moving_averages(
    df: pd.DataFrame,
    columns: list[str],
    window: int = 4,
) -> pd.DataFrame:
    """Add rolling mean columns for specified indicators.

    Args:
        df: DataFrame sorted by week_start.
        columns: Column names to compute moving averages for.
        window: Rolling window size in weeks.

    Returns:
        DataFrame with new columns named '{col}_{window}w_avg'.
    """
    df = df.copy().sort_values("week_start")
    for col in columns:
        if col in df.columns:
            df[f"{col}_{window}w_avg"] = (
                df[col].rolling(window=window, min_periods=1).mean().round(2)
            )
    return df
