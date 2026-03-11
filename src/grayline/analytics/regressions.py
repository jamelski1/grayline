"""OLS regression analysis for strategy effectiveness measurement."""

from dataclasses import dataclass

import pandas as pd
import statsmodels.api as sm


@dataclass
class RegressionResult:
    """Lightweight container for regression output."""

    dep_var: str
    indep_vars: list[str]
    r_squared: float
    adj_r_squared: float
    coefficients: dict[str, float]
    p_values: dict[str, float]
    n_obs: int
    summary_text: str


def run_ols(
    df: pd.DataFrame,
    dep_var: str,
    indep_vars: list[str],
    add_constant: bool = True,
) -> RegressionResult:
    """Run OLS regression and return structured results.

    Args:
        df: Analytic panel DataFrame.
        dep_var: Dependent variable column name.
        indep_vars: List of independent variable column names.
        add_constant: Whether to add a constant term.

    Returns:
        RegressionResult with coefficients, p-values, and fit statistics.
    """
    clean = df[[dep_var, *indep_vars]].dropna()
    y = clean[dep_var]
    X = clean[indep_vars]

    if add_constant:
        X = sm.add_constant(X)

    model = sm.OLS(y, X).fit()

    return RegressionResult(
        dep_var=dep_var,
        indep_vars=indep_vars,
        r_squared=round(model.rsquared, 4),
        adj_r_squared=round(model.rsquared_adj, 4),
        coefficients={k: round(v, 6) for k, v in model.params.items()},
        p_values={k: round(v, 4) for k, v in model.pvalues.items()},
        n_obs=int(model.nobs),
        summary_text=str(model.summary()),
    )


def correlation_matrix(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Compute pairwise correlation matrix for selected columns."""
    return df[columns].corr().round(3)
