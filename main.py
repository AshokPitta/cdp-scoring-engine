"""
DSSA Technical Assessment.

uv run python ./main.py
"""

from datetime import date
import re

from src.utils import load_data, save_output


STATEMENT_1 = "Lorem ipsum dolor sit amet"
STATEMENT_2 = "consectetur adipiscing elit"
STATEMENT_3 = "sed do eiusmod tempor"

CUTOFF_DATE = date(2023, 1, 1)

OUTPUT_FIELDS_CSV = [
    "company_id",
    "row_id",
    "theme",
    "route",
    "score_achieved",
    "maximum_score",
    "c2_dates",
    "c1_company_answer",
    "c3_numbers",
    "statement_1_present",
    "statement_2_present",
    "statement_3_present",
    "c3_numbers_count",
    "c3_numbers_has_even",
    "notes",
]


def normalize_text(value):
    """
    Cleans a string for reliable comparison.
     1) Converts to lowercase
     2) Strips extra whitespace
     3) Returns empty string if input is not a string

    """
    if type(value) is not str:
        return ""
    return " ".join(value.lower().split())


def statement_present_checker(answer, statement):
    """
    Checks if a statement appears anywhere inside an answer
     1) Normalises both strings before comparing
     2) Returns False if answer is empty or invalid
     3) Returns True if statement is found False otherwise

    """
    normalized_answer = normalize_text(answer)
    if not normalized_answer:
        return False
    return normalize_text(statement) in normalized_answer


def parse_date(value):
    """
    Parses a date string into a date object
     1) Supports any separator ("-","/",".", space etc.)
     2) Supports YYYY-MM-DD and DD-MM-YYYY formats
     3) Returns None if input is not a string or cannot be parsed

    """
    if type(value) is not str:
        return None

    normalised = re.sub(r"[^a-zA-Z0-9]", "-", value.strip())

    # YYYY-MM-DD
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", normalised)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return None

    # DD-MM-YYYY
    m = re.fullmatch(r"(\d{2})-(\d{2})-(\d{4})", normalised)
    if m:
        try:
            return date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None

    return None


def normalize_c3_numbers(value):
    """
    Cleans the c3 list (numbers) by keeping only valid numbers
     1) Removes None, booleans and strings
     2) Returns empty list if input is not a list

    """
    if type(value) is not list:
        return []
    return [
        item
        for item in value
        if type(item) in (int, float)
    ]


def format_c3_numbers_to_string(value):
    """
    Converts the raw c3 list (numbers) to a string for the output file
     1) Returns empty string if value is None or empty list
     2) Returns string representation of the list otherwise

    """
    if not value:
        return ""
    return str(value)


def analyze_row(row: dict) -> dict:
    """
    Extracts and analyses all relevant fields from a single row
     1) Parses the date from c2 (dates)
     2) Cleans the c3 list (numbers)
     3) Checks which statements are present in c1 (company answers)
     4) Returns a dictionary of all analysed values

    """
    c1 = row.get("c1") if "c1" in row else None
    c2_raw = row.get("c2") if "c2" in row else None
    c3_raw = row.get("c3") if "c3" in row else None
    parsed_date = parse_date(c2_raw)
    c3_numbers = normalize_c3_numbers(c3_raw)

    c3_numbers_has_even = False
    for n in c3_numbers:
        if n % 2 == 0:
            c3_numbers_has_even = True
            break

    return {
        "c1": c1 if type(c1) is str else None,
        "c2_raw": c2_raw,
        "c3_raw": c3_raw,
        "parsed_date": parsed_date,
        "statement_1_present": statement_present_checker(c1, STATEMENT_1),
        "statement_2_present": statement_present_checker(c1, STATEMENT_2),
        "statement_3_present": statement_present_checker(c1, STATEMENT_3),
        "c3_numbers_count": len(c3_numbers),
        "c3_numbers_has_even": c3_numbers_has_even,
    }


def date_note(c2_raw, parsed_date) -> str:
    """
    Returns a note explaining why a row got non disclosure or Route B
     1) From date missing to c2 was None
     2) From date not parseable to c2 existed but could not be parsed
     3) From date on/before cutoff to date was valid but too old
     4) From empty string to everything was fine. no note needed

    """
    if c2_raw is None:
        return "Date missing."
    if parsed_date is None:
        return "Date not parseable; treated as missing."
    if parsed_date <= CUTOFF_DATE:
        return "Date on/before 2023-01-01."
    return ""


def assemble_output_row(
    company_id,
    row_id,
    theme,
    analysis,
    route,
    score_achieved,
    maximum_score,
    notes,
) -> dict:
    """
    Assembles all scored and analysed values into one output row dictionary.
     1) Direct values (company_id, row_id, theme, route, score_achieved, maximum_score, notes) are passed in as it is
     2) c1 (Company answers), c2 (dates), c3 (numbers) are extracted and formatted from the analysis dictionary
     3) Statement checks, c3_numbers_count, c3_numbers_has_even are pulled from analysis

    """
    return {
        "company_id": company_id,
        "row_id": row_id,
        "theme": theme,
        "route": route,
        "score_achieved": score_achieved,
        "maximum_score": maximum_score,
        "c2_dates": "" if analysis.get("c2_raw") is None else str(analysis.get("c2_raw")),
        "c1_company_answer": analysis.get("c1") or "",
        "c3_numbers": format_c3_numbers_to_string(analysis.get("c3_raw")),
        "statement_1_present": analysis.get("statement_1_present", False),
        "statement_2_present": analysis.get("statement_2_present", False),
        "statement_3_present": analysis.get("statement_3_present", False),
        "c3_numbers_count": analysis.get("c3_numbers_count", 0),
        "c3_numbers_has_even": analysis.get("c3_numbers_has_even", False),
        "notes": notes,
    }


def score_climate_row(company_id, row_id, analysis: dict) -> dict:
    """
    Scores a single row for the Climate Change theme.
     1) Non disclosure (score 0, max 0.5) if date is missing or on/before cutoff
     2) Route A otherwise, with max score of 4:
         i) +3 if statement 2 is present and c3 has more than 3 numbers
        ii) +1 if statement 3 is present and c3 has at least one even number

    """
    parsed_date = analysis["parsed_date"]
    if parsed_date is None or parsed_date <= CUTOFF_DATE:
        return assemble_output_row(
            company_id,
            row_id,
            "Climate Change",
            analysis,
            "Non-disclosure",
            0,
            0.5,
            date_note(analysis.get("c2_raw"), parsed_date),
        )

    score_achieved = 0
    if analysis["statement_2_present"] and analysis["c3_numbers_count"] > 3:
        score_achieved += 3
    if analysis["statement_3_present"] and analysis["c3_numbers_has_even"]:
        score_achieved += 1

    return assemble_output_row(
        company_id,
        row_id,
        "Climate Change",
        analysis,
        "Route A",
        score_achieved,
        4,
        "",
    )


def score_water_row(company_id, row_id, analysis: dict) -> dict:
    """
    Scores a single row for the Water theme.
     1) Non disclosure (score 0, max 0.5) if date is missing
     2) Route B (score 1, max 2) if date is on/before cutoff
     3) Route A otherwise, with max score of 2:
         i) +1 if statement 1 is present and c3 has at least one even number
        ii) +1 if statement 3 is present and c3 has more than 3 numbers

    """
    parsed_date = analysis["parsed_date"]
    if parsed_date is None:
        return assemble_output_row(
            company_id,
            row_id,
            "Water",
            analysis,
            "Non-disclosure",
            0,
            0.5,
            date_note(analysis.get("c2_raw"), parsed_date),
        )

    if parsed_date <= CUTOFF_DATE:
        return assemble_output_row(
            company_id,
            row_id,
            "Water",
            analysis,
            "Route B",
            1,
            2,
            date_note(analysis.get("c2_raw"), parsed_date),
        )

    score_achieved = 0
    if analysis["statement_1_present"] and analysis["c3_numbers_has_even"]:
        score_achieved += 1
    if analysis["statement_3_present"] and analysis["c3_numbers_count"] > 3:
        score_achieved += 1

    return assemble_output_row(
        company_id,
        row_id,
        "Water",
        analysis,
        "Route A",
        score_achieved,
        2,
        "",
    )


def score_all(data: dict) -> list[dict]:
    """
    Processes every company and row in the dataset
     1) Loops through each company and each row
     2) Analyses each row and scores it for whichever themes it belongs to
     3) If a company never selected a theme adds a placeholder Not applicable row
     4) Returns the complete list of all output rows

    """
    output = []
    companies = data.get("companies", {})

    for company_id, company_data in companies.items():
        rows = company_data.get("q_1_1", {})
        company_themes = set()

        for row_id, row in rows.items():
            c4 = row.get("c4")
            themes = c4 if type(c4) is list else []
            company_themes.update(themes)
            analysis = analyze_row(row)

            if "Climate Change" in themes:
                output.append(score_climate_row(company_id, row_id, analysis))
            if "Water" in themes:
                output.append(score_water_row(company_id, row_id, analysis))

        for theme in ("Climate Change", "Water"):
            if theme not in company_themes:
                output.append({
                    "company_id": company_id,
                    "row_id": "N/A",
                    "theme": theme,
                    "route": "Not applicable",
                    "score_achieved": 0,
                    "maximum_score": 0,
                    "c2_dates": "",
                    "c1_company_answer": "",
                    "c3_numbers": "",
                    "statement_1_present": False,
                    "statement_2_present": False,
                    "statement_3_present": False,
                    "c3_numbers_count": 0,
                    "c3_numbers_has_even": False,
                    "notes": "Theme not selected in any row for this company.",
                })

    return output


if __name__ == "__main__":
    data = load_data()
    scores = score_all(data)
    save_output(scores, OUTPUT_FIELDS_CSV)
