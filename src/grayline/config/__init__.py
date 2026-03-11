"""Configuration management for Grayline."""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ANALYTIC_DIR = DATA_DIR / "analytic"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

for d in [RAW_DIR, PROCESSED_DIR, ANALYTIC_DIR, OUTPUTS_DIR / "charts", OUTPUTS_DIR / "reports"]:
    d.mkdir(parents=True, exist_ok=True)
