"""Regression Analysis dashboard page."""

import pandas as pd
import streamlit as st

from grayline.analytics.regressions import correlation_matrix, run_ols
from grayline.dashboard.charts import heatmap
from grayline.dashboard.layout import page_header


def render(panel: pd.DataFrame) -> None:
    page_header(
        "Regression Analysis",
        "Statistical analysis of relationships between policy inputs and strategic outcomes",
    )

    if panel.empty:
        st.warning("No data available.")
        return

    # Correlation matrix
    st.subheader("Indicator Correlation Matrix")

    corr_cols = [
        c for c in [
            "ofac_total_new",
            "ofac_iran_related",
            "oil_revenue_proxy",
            "acled_iran_protest_count",
            "maritime_incident_count",
            "acled_proxy_attack_count",
            "regional_escalation_index",
            "composite_effectiveness_score",
        ]
        if c in panel.columns
    ]

    if len(corr_cols) >= 2:
        corr = correlation_matrix(panel, corr_cols)
        st.plotly_chart(heatmap(corr), use_container_width=True)

    # OLS Regression
    st.subheader("OLS Regression: Proxy Attacks")
    st.caption(
        "Dependent variable: proxy attack count. "
        "Independent variables: sanctions inputs and intermediate indicators."
    )

    dep_var = st.selectbox(
        "Dependent Variable",
        options=[
            "acled_proxy_attack_count",
            "regional_escalation_index",
            "composite_effectiveness_score",
        ],
        index=0,
    )

    available_indep = [
        c for c in [
            "ofac_total_new",
            "ofac_iran_related",
            "sanctions_lag_4w",
            "oil_revenue_proxy",
            "acled_iran_protest_count",
            "maritime_incident_count",
        ]
        if c in panel.columns
    ]

    indep_vars = st.multiselect(
        "Independent Variables",
        options=available_indep,
        default=available_indep[:3] if len(available_indep) >= 3 else available_indep,
    )

    if indep_vars and dep_var:
        try:
            result = run_ols(panel, dep_var, indep_vars)

            col1, col2, col3 = st.columns(3)
            col1.metric("R²", f"{result.r_squared:.4f}")
            col2.metric("Adjusted R²", f"{result.adj_r_squared:.4f}")
            col3.metric("Observations", result.n_obs)

            st.markdown("**Coefficients and Significance**")
            coeff_df = pd.DataFrame({
                "Variable": result.coefficients.keys(),
                "Coefficient": result.coefficients.values(),
                "p-value": [result.p_values.get(k, None) for k in result.coefficients.keys()],
            })
            coeff_df["Significant (p<0.05)"] = coeff_df["p-value"].apply(
                lambda p: "Yes" if p is not None and p < 0.05 else "No"
            )
            st.dataframe(coeff_df, use_container_width=True, hide_index=True)

            with st.expander("Full Regression Summary"):
                st.code(result.summary_text)

        except Exception as e:
            st.error(f"Regression failed: {e}")
    else:
        st.info("Select at least one independent variable to run the regression.")
