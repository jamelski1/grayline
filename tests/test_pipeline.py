"""Tests for the data pipeline."""

import pandas as pd

from grayline.pipelines.build_weekly_panel import build_panel


def test_build_panel_produces_data():
    panel = build_panel()
    assert isinstance(panel, pd.DataFrame)
    assert not panel.empty
    assert "week_start" in panel.columns


def test_panel_has_required_columns():
    panel = build_panel()
    required = [
        "week_start",
        "ofac_total_new",
        "ofac_iran_related",
        "acled_iran_protest_count",
        "acled_proxy_attack_count",
        "oil_revenue_proxy",
        "maritime_incident_count",
        "regional_escalation_index",
        "composite_effectiveness_score",
    ]
    for col in required:
        assert col in panel.columns, f"Missing column: {col}"


def test_panel_derived_columns():
    panel = build_panel()
    assert "four_week_attack_avg" in panel.columns
    assert "four_week_protest_avg" in panel.columns
    assert "sanctions_lag_4w" in panel.columns
