# Grayline

**Strategic Monitoring & Analytics Platform**

Grayline transforms strategy from a narrative exercise into a measurable signal analysis problem. It evaluates whether a policy or strategy is working by tracking quantifiable indicators over time using publicly available data.

## Concept

Most strategic assessments rely on qualitative judgment. Grayline provides a structured, data-driven alternative by modeling strategy as a **signal chain**:

```
Policy Inputs → Intermediate Effects → Strategic Outcomes
```

**Example**: Sanctions pressure → economic strain → reduced proxy activity

The platform pulls public data sources, normalizes them into a unified weekly analytic dataset, tracks leading and lagging indicators, and provides dashboards and regression analysis to help analysts determine whether strategy inputs correlate with desired outcomes.

## Initial Use Case

The initial deployment monitors **Iran/IRGC regional activity**, tracking:

| Layer | Indicators |
|-------|-----------|
| **Inputs** | OFAC sanctions designations (total, Iran-related) |
| **Intermediate** | Oil revenue proxy (Brent crude), Iran domestic protests, maritime incidents |
| **Outcomes** | Proxy group attacks, regional escalation index |
| **Derived** | 4-week moving averages, lagged variables, composite effectiveness score |

The architecture is generic and can support other strategic problems (China deterrence, sanctions regimes, counterterrorism, maritime security, etc.).

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Data Connectors                       │
│  OFAC  │  ACLED  │  FRED  │  World Bank  │  GDELT      │
└────────┬────────┬────────┬──────────────┬───────────────┘
         │        │        │              │
         ▼        ▼        ▼              ▼
┌─────────────────────────────────────────────────────────┐
│              Weekly Panel Builder Pipeline               │
│  fetch → normalize → merge → derive features → save     │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Analytics Engine                        │
│  Moving Averages │ Lag Features │ OLS │ Composite Score  │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 Streamlit Dashboard                       │
│  Executive Summary │ Inputs │ Intermediate │ Outcomes    │
│  Regression Analysis │ Data Quality                      │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
grayline/
├── app/
│   ├── main.py                          # Streamlit entry point
│   └── pages/
│       ├── executive_summary.py         # Status cards, trend charts, composite score
│       ├── inputs.py                    # Sanctions pressure tracking
│       ├── intermediate_effects.py      # Leading indicators
│       ├── outcomes.py                  # Strategic outcome measurement
│       ├── regression_analysis.py       # OLS regression & correlation
│       └── data_quality.py             # Data freshness & completeness
├── src/
│   └── grayline/
│       ├── config/                      # Settings, paths, env loading
│       ├── connectors/                  # Modular data source connectors
│       │   ├── base.py                  # Abstract base connector
│       │   ├── ofac.py                  # OFAC sanctions data
│       │   ├── acled.py                 # ACLED conflict & protest data
│       │   ├── fred.py                  # FRED economic indicators
│       │   ├── world_bank.py            # World Bank indicators
│       │   └── gdelt.py                # GDELT media/event signals
│       ├── pipelines/
│       │   └── build_weekly_panel.py    # Core data pipeline
│       ├── analytics/
│       │   ├── moving_averages.py       # Rolling averages
│       │   ├── lag_features.py          # Lagged variables
│       │   ├── regressions.py           # OLS regression
│       │   └── composite_score.py       # Effectiveness scoring
│       ├── models/
│       │   └── indicator_schema.py      # Pydantic schemas & indicator registry
│       ├── dashboard/
│       │   ├── charts.py                # Plotly chart builders
│       │   └── layout.py               # Shared UI components
│       └── utils/
│           ├── logging.py               # Logging config
│           └── dates.py                 # Date utilities
├── data/
│   ├── raw/                             # Raw data snapshots
│   ├── processed/                       # Intermediate processed data
│   └── analytic/                        # Weekly panel output
├── outputs/
│   ├── charts/                          # Exported charts
│   └── reports/                         # Generated reports
├── tests/                               # pytest test suite
├── pyproject.toml                       # Project config & dependencies
├── .env.example                         # API key template
└── .gitignore
```

## Setup

### Prerequisites

- Python 3.12+
- pip or uv

### Installation

```bash
# Clone the repository
git clone <repo-url> && cd grayline

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -e ".[dev]"
```

### API Credentials (Optional)

The dashboard works immediately with sample data. To enable live data:

```bash
cp .env.example .env
# Edit .env with your API keys
```

| Source | Key Required | How to Get |
|--------|-------------|-----------|
| OFAC | No | Public CSV download |
| ACLED | Yes | [Register at acleddata.com](https://acleddata.com/) |
| FRED | Yes | [Request at fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| World Bank | No | Public API |
| GDELT | No | Public API |

## Running the Dashboard

```bash
streamlit run app/main.py
```

The dashboard will open at `http://localhost:8501`.

On first run, the platform generates realistic sample data so all charts and analytics are immediately functional.

## Running Tests

```bash
pytest
```

## Key Design Decisions

1. **Connector pattern**: Each data source is a self-contained module with `fetch()`, `normalize()`, and `load_sample()` methods, making it straightforward to add new sources.

2. **Graceful degradation**: Every connector falls back to sample data if the live API is unavailable, ensuring the dashboard always works.

3. **Weekly alignment**: All data is normalized to Monday-start weeks, creating a consistent temporal join key across disparate sources.

4. **Modular analytics**: Moving averages, lag features, regressions, and composite scoring are independent functions that analysts can mix and reconfigure.

5. **Signal chain model**: The UI is structured around the Input → Intermediate → Outcome framework, reinforcing the analytical model.

## Roadmap

- [ ] DuckDB/SQLite persistent storage layer
- [ ] Automated weekly data refresh (cron/scheduler)
- [ ] Additional connectors (UN OCHA, maritime AIS, SIPRI arms data)
- [ ] Alerting system for threshold breaches
- [ ] Multi-strategy support (China, counterterrorism, maritime security)
- [ ] Export to PDF/PowerPoint briefing format
- [ ] User-configurable indicator weights
- [ ] Time-series forecasting (ARIMA, Prophet)
- [ ] Role-based access control for team deployments
