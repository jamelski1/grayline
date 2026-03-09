"""Composite effectiveness scoring.

Combines multiple indicators into a single strategy effectiveness score
using configurable weights and normalization.
"""

import numpy as np
import pandas as pd


def min_max_normalize(series: pd.Series) -> pd.Series:
    """Normalize a series to [0, 1] range."""
    smin, smax = series.min(), series.max()
    if smax == smin:
        return pd.Series(0.5, index=series.index)
    return (series - smin) / (smax - smin)


def compute_composite_score(
    df: pd.DataFrame,
    positive_cols: list[str] | None = None,
    negative_cols: list[str] | None = None,
    weights: dict[str, float] | None = None,
) -> pd.Series:
    """Compute a composite strategy effectiveness score (0-100).

    Positive indicators (higher = strategy working) are added.
    Negative indicators (higher = strategy failing) are subtracted.

    Args:
        df: Analytic panel DataFrame.
        positive_cols: Columns where higher values indicate effectiveness.
        negative_cols: Columns where higher values indicate ineffectiveness.
        weights: Optional per-column weights (default equal weight).

    Returns:
        Series of composite scores scaled 0-100.
    """
    if positive_cols is None:
        positive_cols = [
            "ofac_total_new",
            "acled_iran_protest_count",
        ]
    if negative_cols is None:
        negative_cols = [
            "acled_proxy_attack_count",
            "regional_escalation_index",
            "oil_revenue_proxy",
        ]

    all_cols = positive_cols + negative_cols
    if weights is None:
        weights = {c: 1.0 for c in all_cols}

    score = pd.Series(0.0, index=df.index)

    for col in positive_cols:
        if col in df.columns:
            normed = min_max_normalize(df[col].fillna(0))
            score += normed * weights.get(col, 1.0)

    for col in negative_cols:
        if col in df.columns:
            normed = min_max_normalize(df[col].fillna(0))
            score -= normed * weights.get(col, 1.0)

    # Rescale to 0-100
    score = min_max_normalize(score) * 100
    return score.round(1)
