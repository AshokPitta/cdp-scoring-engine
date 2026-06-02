# Solution

This document explains how the scoring system is built, the decisions made along the way, and why. It is meant to be read alongside `main.py`, `src/utils.py`, and the tests.

## Overview

The task is to score eight companies' `q_1_1` responses against two independent criteria — **Climate Change** and **Water** — and produce a per-row CSV that a non-technical reviewer can read and validate.

The solution is built in three layers:

1. **IO layer** (`src/utils.py`) — loads `data.json`, writes `output.csv`. Kept deliberately thin so the scoring logic has no knowledge of file paths or formats.
2. **Analysis layer** (`analyze_row` in `main.py`) — extracts and cleans the four fields of a single row once, returning a normalised dictionary. This separates *understanding* a row from *scoring* it.
3. **Scoring layer** (`score_climate_row`, `score_water_row`) — applies each theme's route logic to an already-analysed row.

The entry point (`score_all`) walks every company and row, dispatches to the right scoring function per theme, and handles the company-level "Not applicable" case.

## How a row flows through the system

```
row (raw dict)
   │
   ▼
analyze_row()  →  parses date, cleans c3, checks the three statements
   │
   ▼
score_climate_row() / score_water_row()   (called per theme tagged in c4)
   │
   ▼
assemble_output_row()  →  flat dict matching the CSV columns
```

Scoring functions never touch the raw row directly — they only see the analysed output. This keeps the route logic readable and makes it trivial to test each piece in isolation.

## Routing logic

Each theme is a small decision tree driven by the date in `c2`:

**Climate Change**
- No date / unparseable date / date on or before 2023-01-01 → **Non-disclosure** (0 / 0.5)
- Date after 2023-01-01 → **Route A** (up to 4):
  - +3 if statement 2 present **and** `c3` has more than 3 numbers
  - +1 if statement 3 present **and** `c3` has at least one even number
- Theme never selected by the company → **Not applicable** (0 / 0)

**Water**
- No date provided → **Non-disclosure** (0 / 0.5)
- Date on or before 2023-01-01 → **Route B** (1 / 2)
- Date after 2023-01-01 → **Route A** (up to 2):
  - +1 if statement 1 present **and** `c3` has at least one even number
  - +1 if statement 3 present **and** `c3` has more than 3 numbers
- Theme never selected by the company → **Not applicable** (0 / 0)

The one subtlety here is that **Climate Change and Water treat missing-vs-old dates differently.** Climate Change collapses both "no date" and "date too old" into Non-disclosure, because the brief defines its Non-disclosure route as covering both. Water splits them: a missing date is Non-disclosure (0 / 0.5), while an old-but-present date earns Route B (1 / 2). The code mirrors the brief exactly rather than trying to unify the two themes.

## Data quality handling

The dataset is raw and deliberately messy. Each issue is handled at the analysis layer so the scoring logic only ever sees clean values:

| Issue (seen in data) | Where | Handling |
|---|---|---|
| Date with slashes (`2024/06/01`) | Company 4 | `parse_date` replaces any non-alphanumeric separator with `-` before parsing |
| Fully uppercase `c1` | Company 4 | `normalize_text` lowercases both sides before matching |
| Extra / irregular whitespace in `c1` | Company 6 | `normalize_text` collapses runs of whitespace via `split()` + `join()` |
| `null` inside the `c3` list | Companies 4, 6 | `normalize_c3_numbers` keeps only `int`/`float`, dropping `None` |
| `c2: null` (field shown, not answered) | Companies 4, 7 | Treated as missing date → routed per theme |
| `c3` key absent entirely | Company 8 | `.get()` returns `None` → normalised to empty list |
| Booleans masquerading as numbers | guarded | `normalize_c3_numbers` excludes `bool` implicitly by checking exact `type` |

### Two design choices worth calling out

**1. `type(x) is int` rather than `isinstance`.** In Python `bool` is a subclass of `int`, so `isinstance(True, int)` is `True`. Using exact type checks in `normalize_c3_numbers` means a stray `true` in a number list is correctly discarded rather than counted as `1`. This is intentional — environmental disclosure numbers should be real numbers.

**2. Date parsing is permissive but bounded.** `parse_date` accepts any separator and both `YYYY-MM-DD` and `DD-MM-YYYY` orderings, but returns `None` rather than guessing on anything ambiguous or invalid. A `None` date always routes to the safe (lower-scoring) branch, so malformed data can never inflate a score.

## Output design

The CSV is built for a non-technical reviewer, not just for machines. Beyond the score itself, every row carries the *evidence* behind the score:

- `statement_1/2/3_present` — which lorem ipsum statements were detected
- `c3_numbers_count` and `c3_numbers_has_even` — the two properties the criteria depend on
- `notes` — a plain-English reason whenever a row lands on Non-disclosure or Route B (e.g. "Date missing.", "Date on/before 2023-01-01.")

This means a reviewer can look at any score and reconstruct *why* it was awarded without reading the code — which is exactly what the Company 5 QA query asks for.

## Testing

Tests are split by concern:

- **Unit tests** on the pure helpers (`normalize_text`, `statement_present_checker`, `parse_date`, `normalize_c3_numbers`) cover the data-quality edge cases directly — uppercase, whitespace, slashes, nulls, non-strings.
- **Scoring tests** on `score_climate_row` and `score_water_row` verify each route and each scoring condition independently, including the boundary at exactly 3 numbers (which should *not* score, since the criterion is "more than 3").

The boundary cases are deliberate: the "more than 3" threshold and the cutoff date are the two places where an off-by-one error is most likely, so they get explicit coverage.

## QA query (Company 5)

The full written answer is in `qa_answers.md`. In short: both of Company 5's rows entered Route A correctly (valid recent dates) but scored 0 because neither row contained the third statement *and* neither number list was long enough to trigger the 3-point condition — `[1, 2, 3]` has exactly 3 elements, one short of the "more than 3" threshold. The QA response also flags that the strict threshold and the lack of partial credit are worth raising with the methodology team, since a near-miss currently scores identically to a non-response.

## Assumptions

- "After 2023-01-01" is treated as strictly after (the cutoff date itself scores as Non-disclosure / Route B), matching the brief's "on or before" wording for the lower routes.
- A company is "Not applicable" for a theme only if *no* row selects that theme; a single tagged row puts the whole company in scope for that theme.
- Statement matching is substring-based after normalisation, so a longer answer containing the statement still counts.
