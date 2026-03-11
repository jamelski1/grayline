"""Data Quality dashboard page."""

import pandas as pd
import streamlit as st

from grayline.dashboard.layout import metric_row, page_header
from grayline.pipelines.build_weekly_panel import OUTPUT_PATH


def render(panel: pd.DataFrame) -> None:
    page_header(
        "Data Quality",
        "Monitoring data freshness, completeness, and source status",
    )

    if panel.empty:
        st.warning("No data available.")
        return

    # Overview metrics
    total_weeks = len(panel)
    latest_week = panel["week_start"].max()
    earliest_week = panel["week_start"].min()
    total_cols = len(panel.columns)

    metric_row([
        {"label": "Total Weeks", "value": str(total_weeks)},
        {"label": "Date Range", "value": f"{earliest_week.strftime('%Y-%m-%d')} → {latest_week.strftime('%Y-%m-%d')}"},
        {"label": "Indicators", "value": str(total_cols - 1)},  # minus week_start
        {"label": "Panel File", "value": str(OUTPUT_PATH.name)},
    ])

    st.markdown("")

    # Completeness
    st.subheader("Column Completeness")
    completeness = []
    for col in panel.columns:
        if col == "week_start":
            continue
        non_null = panel[col].notna().sum()
        pct = non_null / total_weeks * 100
        completeness.append({
            "Indicator": col,
            "Non-Null Rows": non_null,
            "Total Rows": total_weeks,
            "Completeness (%)": round(pct, 1),
        })

    comp_df = pd.DataFrame(completeness).sort_values("Completeness (%)")
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # Source status
    st.subheader("Data Source Status")
    sources = {
        "OFAC": {"columns": ["ofac_total_new", "ofac_iran_related"], "mode": "Sample Data"},
        "ACLED": {"columns": ["acled_iran_protest_count", "acled_proxy_attack_count"], "mode": "Sample Data"},
        "FRED": {"columns": ["oil_revenue_proxy"], "mode": "Sample Data"},
        "World Bank / Maritime": {"columns": ["maritime_incident_count"], "mode": "Sample Data"},
        "GDELT": {"columns": ["regional_escalation_index"], "mode": "Sample Data"},
    }

    for name, info in sources.items():
        available = [c for c in info["columns"] if c in panel.columns]
        status = "Connected" if available else "Missing"
        icon = "●" if available else "○"
        color = "#27AE60" if available else "#C0392B"
        st.markdown(
            f'<span style="color:{color}; font-weight:600">{icon}</span> '
            f'**{name}** — {info["mode"]} — '
            f'{len(available)}/{len(info["columns"])} columns available',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # Summary statistics
    st.subheader("Descriptive Statistics")
    numeric_cols = panel.select_dtypes(include="number").columns
    st.dataframe(
        panel[numeric_cols].describe().round(2).T,
        use_container_width=True,
    )

    # Data notes
    st.subheader("Notes")
    st.markdown("""
    - **Sample Data Mode**: All connectors are currently using generated sample data.
      Add API keys to `.env` to enable live data fetching.
    - **Refresh**: Click "Rebuild Data Panel" in the sidebar to regenerate the dataset.
    - **Weekly Alignment**: All data is aligned to Monday-start weeks (ISO week convention).
    - **Missing Values**: Missing values in the panel are filled with 0 for numeric columns.
      Lagged and derived columns may contain NaN for initial periods.
    """)
