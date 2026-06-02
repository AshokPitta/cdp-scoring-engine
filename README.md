# CDP Disclosure Scoring System

A technical assessment project built for **CDP (Carbon Disclosure Project)** : an automated scoring engine that evaluates company climate and water disclosure responses based on a multi-route decision tree logic.

---

## Overview

CDP collects environmental disclosure data from companies worldwide. This project implements a scoring pipeline that:

- Ingests structured company response data (JSON)
- Routes each response through a decision tree (Not Applicable → Non-Disclosure → Route A)
- Applies weighted scoring criteria per disclosure topic (Climate Change, Water)
- Handles real-world data quality issues (nulls, inconsistent date formats, casing, whitespace)
- Outputs a clean scored CSV with per-company results

---

## Scoring Logic

Each company response is evaluated per topic using this decision tree:

```
Did the company select this topic?
│
├── NO  → Not Applicable (0/0)
│
└── YES → Did they provide a date after 1 Jan 2023?
          │
          ├── NO / missing date → Non-Disclosure (0/0.5)
          │
          └── YES → Route A (up to 4 points):
                    • +3 pts: written answer contains target phrase AND
                              numeric list has more than 3 elements
                    • +1 pt:  written answer contains secondary phrase AND
                              numeric list contains at least one even number
```

---

## Project Structure

```
cdp-scoring-system/
├── main.py              # Entry point — orchestrates scoring pipeline
├── pyproject.toml       # Project dependencies and metadata
├── README.md
├── SETUP.md             # Setup and run instructions
├── qa_answers.md        # QA analysis and methodology notes
├── src/
│   ├── __init__.py
│   └── utils.py         # Core scoring logic and helpers
├── local/
│   └── data.json        # Sample input data (8 companies)
└── tests/
    ├── test_main.py
    └── test_utils.py
```

---

## Data Quality Handling

The pipeline robustly handles the following real-world data issues found in the input:

| Issue | Handling |
|---|---|
| Date with slashes (`2024/06/01`) | Normalised to `-` before parsing |
| Fully uppercase `c1` field | Case-insensitive phrase matching |
| `null` values inside `c3` list | Filtered out before numeric checks |
| Extra whitespace in `c1` | Collapsed before matching |
| `c2: null` (missing date) | Routed to Non-Disclosure |
| `c3` key absent entirely | Treated as empty list |

---

## Setup & Run

```bash
# Install dependencies
uv sync

# Run the scoring pipeline
uv run python main.py

# Run tests
uv run pytest tests/ -v
```

Output is saved to `local/output.csv`.

See [SETUP.md](./SETUP.md) for detailed environment setup instructions.

---

## Tech Stack

- **Python 3.11+**
- **uv** — fast Python package manager
- **pytest** — unit and integration testing
- **JSON → CSV** pipeline with custom validation logic

---

## Key Features

- Clean separation of concerns — pipeline orchestration in `main.py`, logic in `src/utils.py`
- Full test coverage across all scoring routes and edge cases
- Handles 8 companies with varied data quality issues
- Deterministic, reproducible output

---

## Author

**Ashok Pitta** — MSc Artificial Intelligence, University of Sheffield  
[LinkedIn](https://linkedin.com/in/ashok-pitta-ai) · [GitHub](https://github.com/ashok-pitta)
