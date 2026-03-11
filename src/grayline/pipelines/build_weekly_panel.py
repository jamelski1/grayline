"""Build the unified weekly analytic panel from all data connectors.

This is the core data pipeline that:
1. Fetches/loads data from each connector
2. Merges into a single weekly panel
3. Adds derived features (moving averages, lags, composite score)
4. Saves to data/analytic/weekly_panel.csv
"""

import logging

import pandas as pd

from grayline.analytics.composite_score import compute_composite_score
from grayline.analytics.lag_features import add_lag_features
from grayline.analytics.moving_averages import add_moving_averages
from grayline.config import ANALYTIC_DIR
from grayline.config.settings import settings
from grayline.connectors.acled import ACLEDConnector
from grayline.connectors.fred import FREDConnector
from grayline.connectors.gdelt import GDELTConnector
from grayline.connectors.ofac import OFACConnector
from grayline.connectors.world_bank import WorldBankConnector

logger = logging.getLogger(__name__)

OUTPUT_PATH = ANALYTIC_DIR / "weekly_panel.csv"


def build_panel(start_date: str | None = None, end_date: str | None = None) -> pd.DataFrame:
    """Build the complete weekly analytic panel.

    Args:
        start_date: Panel start date (YYYY-MM-DD). Defaults to settings.
        end_date: Panel end date. Defaults to today.

    Returns:
        Complete weekly panel DataFrame.
    """
    if start_date is None:
        start_date = settings.panel_start_date
    if end_date is None:
        end_date = pd.Timestamp.now().strftime("%Y-%m-%d")

    logger.info("Building weekly panel: %s to %s", start_date, end_date)

    # Fetch data from all connectors (with fallback to sample data)
    connectors = [
        OFACConnector(),
        ACLEDConnector(),
        FREDConnector(),
        WorldBankConnector(),
        GDELTConnector(),
    ]

    frames = []
    for conn in connectors:
        logger.info("Loading data from %s connector", conn.name)
        df = conn.fetch_or_fallback(start_date, end_date)
        if not df.empty and "week_start" in df.columns:
            df["week_start"] = pd.to_datetime(df["week_start"])
            frames.append(df)

    if not frames:
        logger.error("No data loaded from any connector")
        return pd.DataFrame()

    # Merge all frames on week_start
    panel = frames[0]
    for df in frames[1:]:
        panel = panel.merge(df, on="week_start", how="outer")

    panel = panel.sort_values("week_start").reset_index(drop=True)

    # Fill missing numeric values
    numeric_cols = panel.select_dtypes(include="number").columns
    panel[numeric_cols] = panel[numeric_cols].fillna(0)

    # Add derived features
    panel = add_moving_averages(
        panel,
        columns=["acled_proxy_attack_count", "acled_iran_protest_count"],
        window=4,
    )
    # Rename to match schema
    rename_map = {
        "acled_proxy_attack_count_4w_avg": "four_week_attack_avg",
        "acled_iran_protest_count_4w_avg": "four_week_protest_avg",
    }
    panel = panel.rename(columns=rename_map)

    panel = add_lag_features(panel, columns=["ofac_total_new"], lags=[4])
    if "ofac_total_new_lag_4w" in panel.columns:
        panel = panel.rename(columns={"ofac_total_new_lag_4w": "sanctions_lag_4w"})

    panel["composite_effectiveness_score"] = compute_composite_score(panel)

    # Save
    panel.to_csv(OUTPUT_PATH, index=False)
    logger.info("Weekly panel saved: %s (%d rows)", OUTPUT_PATH, len(panel))

    return panel


def load_panel() -> pd.DataFrame:
    """Load the weekly panel from disk, building it if necessary."""
    if OUTPUT_PATH.exists():
        panel = pd.read_csv(OUTPUT_PATH, parse_dates=["week_start"])
        if not panel.empty:
            return panel

    return build_panel()
