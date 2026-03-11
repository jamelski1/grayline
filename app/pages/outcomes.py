"""Outcomes dashboard page — strategic outcome indicators."""

import pandas as pd
import streamlit as st

from grayline.dashboard.charts import dual_axis, time_series
from grayline.dashboard.layout import metric_row, page_header


def render(panel: pd.DataFrame) -> None:
    page_header(
        "Strategic Outcomes",
        "Lagging indicators that measure whether strategy objectives are being achieved",
    )

    if panel.empty:
        st.warning("No data available.")
        return

    latest = panel.iloc[-1]
    prev_4w = panel.tail(5).iloc[0] if len(panel) >= 5 else latest

    metric_row([
        {
            "label": "Proxy Attacks (latest)",
            "value": f"{latest.get('acled_proxy_attack_count', 0):.0f}",
            "delta": f"{latest.get('acled_proxy_attack_count', 0) - prev_4w.get('acled_proxy_attack_count', 0):+.0f} vs 4w ago",
            "delta_color": "inverse",
        },
        {
            "label": "4-Week Attack Avg",
            "value": f"{latest.get('four_week_attack_avg', 0):.1f}",
            "delta": f"{latest.get('four_week_attack_avg', 0) - prev_4w.get('four_week_attack_avg', 0):+.1f} vs 4w ago",
            "delta_color": "inverse",
        },
        {
            "label": "Escalation Index",
            "value": f"{latest.get('regional_escalation_index', 0):.1f}",
            "delta": f"{latest.get('regional_escalation_index', 0) - prev_4w.get('regional_escalation_index', 0):+.1f} vs 4w ago",
            "delta_color": "inverse",
        },
    ])

    st.markdown("")

    st.plotly_chart(
        time_series(
            panel,
            ["acled_proxy_attack_count", "four_week_attack_avg"],
            labels={
                "acled_proxy_attack_count": "Weekly Proxy Attacks",
                "four_week_attack_avg": "4-Week Average",
            },
            title="Iran-Linked Proxy Attack Activity",
        ),
        use_container_width=True,
    )

    st.plotly_chart(
        time_series(
            panel,
            ["regional_escalation_index"],
            labels={"regional_escalation_index": "Escalation Index"},
            title="Regional Escalation Index (GDELT-derived)",
        ),
        use_container_width=True,
    )

    st.subheader("Input → Outcome Lag Analysis")
    st.caption("Do sanctions designations (input) correlate with reduced proxy attacks (outcome) after a lag?")

    if "sanctions_lag_4w" in panel.columns:
        st.plotly_chart(
            dual_axis(
                panel,
                col_left="sanctions_lag_4w",
                col_right="acled_proxy_attack_count",
                label_left="OFAC Designations (4-week lag)",
                label_right="Proxy Attacks",
                title="Lagged Sanctions Input vs. Proxy Attacks",
            ),
            use_container_width=True,
        )
