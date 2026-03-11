"""Inputs dashboard page — tracks policy input indicators."""

import pandas as pd
import streamlit as st

from grayline.dashboard.charts import bar_chart, time_series, COLORS
from grayline.dashboard.layout import metric_row, page_header


def render(panel: pd.DataFrame) -> None:
    page_header(
        "Policy Inputs",
        "Tracking sanctions pressure and other policy actions as strategy inputs",
    )

    if panel.empty:
        st.warning("No data available.")
        return

    latest = panel.iloc[-1]
    recent_8w = panel.tail(8)

    metric_row([
        {
            "label": "Total OFAC Designations (8w)",
            "value": f"{recent_8w['ofac_total_new'].sum():.0f}",
        },
        {
            "label": "Iran-Related (8w)",
            "value": f"{recent_8w['ofac_iran_related'].sum():.0f}",
        },
        {
            "label": "Iran Share",
            "value": f"{(recent_8w['ofac_iran_related'].sum() / max(recent_8w['ofac_total_new'].sum(), 1) * 100):.0f}%",
        },
        {
            "label": "Latest Week",
            "value": f"{latest['ofac_total_new']:.0f} total / {latest['ofac_iran_related']:.0f} Iran",
        },
    ])

    st.markdown("")

    st.plotly_chart(
        time_series(
            panel,
            ["ofac_total_new", "ofac_iran_related"],
            labels={
                "ofac_total_new": "All New Designations",
                "ofac_iran_related": "Iran-Related",
            },
            title="Weekly OFAC Designation Activity",
        ),
        use_container_width=True,
    )

    st.subheader("Weekly Breakdown")
    st.plotly_chart(
        bar_chart(
            panel.tail(26),
            x_col="week_start",
            y_col="ofac_total_new",
            title="New Designations — Last 26 Weeks",
            color=COLORS["accent"],
        ),
        use_container_width=True,
    )

    with st.expander("Raw Input Data"):
        display_cols = ["week_start", "ofac_total_new", "ofac_iran_related"]
        available = [c for c in display_cols if c in panel.columns]
        st.dataframe(
            panel[available].tail(26).sort_values("week_start", ascending=False),
            use_container_width=True,
            hide_index=True,
        )
