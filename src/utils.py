"""IO helpers for the DSSA assessment."""

import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "local" / "data.json"
OUTPUT_PATH = PROJECT_ROOT / "local" / "output.csv"


def load_data() -> dict:
    """Load the raw company response data."""
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_output(output: list[dict], fields: list[str]) -> None:
    """Write the scoring output to a CSV file in the local folder."""
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)