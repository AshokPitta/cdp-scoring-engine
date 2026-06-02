"""Tests for the DSSA assessment scoring logic."""

from datetime import date
import pytest
from main import (
    normalize_text,
    statement_present_checker,
    parse_date,
    normalize_c3_numbers,
    format_c3_numbers_to_string,
    analyze_row,
    score_climate_row,
    score_water_row,
)


# ── normalize_text ────────────────────────────────────────────────────────────

def test_normalize_text_lowercases():
    assert normalize_text("HELLO WORLD") == "hello world"

def test_normalize_text_collapses_whitespace():
    assert normalize_text("  hello   world  ") == "hello world"

def test_normalize_text_non_string_returns_empty():
    assert normalize_text(None) == ""
    assert normalize_text(123) == ""
    assert normalize_text([]) == ""

def test_normalize_text_empty_string():
    assert normalize_text("") == ""


# ── statement_present_checker ─────────────────────────────────────────────────

def test_statement_present_checker_found():
    assert statement_present_checker("Lorem ipsum dolor sit amet", "Lorem ipsum dolor sit amet") is True

def test_statement_present_checker_found_in_longer_text():
    assert statement_present_checker(
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit",
        "consectetur adipiscing elit"
    ) is True

def test_statement_present_checker_case_insensitive():
    assert statement_present_checker("LOREM IPSUM DOLOR SIT AMET", "lorem ipsum dolor sit amet") is True

def test_statement_present_checker_not_found():
    assert statement_present_checker("Lorem ipsum dolor sit amet", "sed do eiusmod tempor") is False

def test_statement_present_checker_empty_answer():
    assert statement_present_checker("", "lorem ipsum") is False

def test_statement_present_checker_none_answer():
    assert statement_present_checker(None, "lorem ipsum") is False


# ── parse_date ────────────────────────────────────────────────────────────────

def test_parse_date_iso_format():
    assert parse_date("2024-05-15") == date(2024, 5, 15)

def test_parse_date_slash_format():
    assert parse_date("2024/06/01") == date(2024, 6, 1)

def test_parse_date_dd_mm_yyyy():
    assert parse_date("15-06-2024") == date(2024, 6, 15)

def test_parse_date_dot_separator():
    assert parse_date("2024.06.01") == date(2024, 6, 1)

def test_parse_date_none_returns_none():
    assert parse_date(None) is None

def test_parse_date_invalid_string_returns_none():
    assert parse_date("not-a-date") is None

def test_parse_date_invalid_date_returns_none():
    assert parse_date("2024-13-01") is None


# ── normalize_c3_numbers ──────────────────────────────────────────────────────

def test_normalize_c3_numbers_filters_none():
    assert normalize_c3_numbers([1, None, 2, None, 3]) == [1, 2, 3]

def test_normalize_c3_numbers_filters_booleans():
    assert normalize_c3_numbers([1, True, 2, False, 3]) == [1, 2, 3]

def test_normalize_c3_numbers_filters_strings():
    assert normalize_c3_numbers([1, "two", 3]) == [1, 3]

def test_normalize_c3_numbers_keeps_floats():
    assert normalize_c3_numbers([1, 2.5, 3]) == [1, 2.5, 3]

def test_normalize_c3_numbers_non_list_returns_empty():
    assert normalize_c3_numbers(None) == []
    assert normalize_c3_numbers("not a list") == []

def test_normalize_c3_numbers_empty_list():
    assert normalize_c3_numbers([]) == []


# ── format_c3_numbers_to_string ───────────────────────────────────────────────

def test_format_c3_numbers_to_string_list():
    assert format_c3_numbers_to_string([2, 4, 6, 8]) == "[2, 4, 6, 8]"

def test_format_c3_numbers_to_string_none():
    assert format_c3_numbers_to_string(None) == ""

def test_format_c3_numbers_to_string_empty_list():
    assert format_c3_numbers_to_string([]) == ""


# ── analyze_row ───────────────────────────────────────────────────────────────

def test_analyze_row_all_statements_present():
    row = {
        "c1": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor",
        "c2": "2024-05-15",
        "c3": [2, 4, 6, 8],
    }
    result = analyze_row(row)
    assert result["statement_1_present"] is True
    assert result["statement_2_present"] is True
    assert result["statement_3_present"] is True
    assert result["c3_numbers_count"] == 4
    assert result["c3_numbers_has_even"] is True
    assert result["parsed_date"] == date(2024, 5, 15)

def test_analyze_row_missing_c3():
    row = {"c1": "Lorem ipsum dolor sit amet", "c2": "2024-01-01"}
    result = analyze_row(row)
    assert result["c3_numbers_count"] == 0
    assert result["c3_numbers_has_even"] is False

def test_analyze_row_null_c2():
    row = {"c1": "some text", "c2": None, "c3": [1, 2, 3]}
    result = analyze_row(row)
    assert result["parsed_date"] is None

def test_analyze_row_all_odd_c3():
    row = {"c1": "text", "c2": "2024-01-01", "c3": [1, 3, 5, 7]}
    result = analyze_row(row)
    assert result["c3_numbers_has_even"] is False


# ── score_climate_row ─────────────────────────────────────────────────────────

def test_score_climate_row_full_score():
    analysis = {
        "parsed_date": date(2024, 5, 15),
        "c2_raw": "2024-05-15",
        "c1": "lorem ipsum",
        "c3_raw": [2, 4, 6, 8],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": True,
        "c3_numbers_count": 4,
        "c3_numbers_has_even": True,
    }
    result = score_climate_row("1", "r1", analysis)
    assert result["score_achieved"] == 4
    assert result["maximum_score"] == 4
    assert result["route"] == "Route A"

def test_score_climate_row_non_disclosure_missing_date():
    analysis = {
        "parsed_date": None,
        "c2_raw": None,
        "c1": "lorem ipsum",
        "c3_raw": [2, 4, 6, 8],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": True,
        "c3_numbers_count": 4,
        "c3_numbers_has_even": True,
    }
    result = score_climate_row("1", "r1", analysis)
    assert result["score_achieved"] == 0
    assert result["maximum_score"] == 0.5
    assert result["route"] == "Non-disclosure"
    assert result["notes"] == "Date missing."

def test_score_climate_row_non_disclosure_old_date():
    analysis = {
        "parsed_date": date(2022, 6, 15),
        "c2_raw": "2022-06-15",
        "c1": "lorem ipsum",
        "c3_raw": [2, 4, 6, 8],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": True,
        "c3_numbers_count": 4,
        "c3_numbers_has_even": True,
    }
    result = score_climate_row("1", "r1", analysis)
    assert result["route"] == "Non-disclosure"
    assert result["score_achieved"] == 0

def test_score_climate_row_partial_score():
    analysis = {
        "parsed_date": date(2024, 5, 15),
        "c2_raw": "2024-05-15",
        "c1": "lorem ipsum",
        "c3_raw": [1, 3, 5, 7, 9],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": False,
        "c3_numbers_count": 5,
        "c3_numbers_has_even": False,
    }
    result = score_climate_row("1", "r1", analysis)
    assert result["score_achieved"] == 3
    assert result["route"] == "Route A"

def test_score_climate_row_zero_c3_count():
    analysis = {
        "parsed_date": date(2024, 5, 15),
        "c2_raw": "2024-05-15",
        "c1": "lorem ipsum",
        "c3_raw": [1, 2, 3],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": True,
        "c3_numbers_count": 3,
        "c3_numbers_has_even": True,
    }
    result = score_climate_row("1", "r1", analysis)
    assert result["score_achieved"] == 1  # only +1 from statement_3 + even


# ── score_water_row ───────────────────────────────────────────────────────────

def test_score_water_row_full_score():
    analysis = {
        "parsed_date": date(2024, 5, 15),
        "c2_raw": "2024-05-15",
        "c1": "lorem ipsum",
        "c3_raw": [2, 4, 6, 8],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": True,
        "c3_numbers_count": 4,
        "c3_numbers_has_even": True,
    }
    result = score_water_row("1", "r1", analysis)
    assert result["score_achieved"] == 2
    assert result["maximum_score"] == 2
    assert result["route"] == "Route A"

def test_score_water_row_non_disclosure_missing_date():
    analysis = {
        "parsed_date": None,
        "c2_raw": None,
        "c1": "lorem ipsum",
        "c3_raw": [2, 4, 6, 8],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": True,
        "c3_numbers_count": 4,
        "c3_numbers_has_even": True,
    }
    result = score_water_row("1", "r1", analysis)
    assert result["score_achieved"] == 0
    assert result["maximum_score"] == 0.5
    assert result["route"] == "Non-disclosure"
    assert result["notes"] == "Date missing."

def test_score_water_row_route_b_old_date():
    analysis = {
        "parsed_date": date(2022, 6, 15),
        "c2_raw": "2022-06-15",
        "c1": "lorem ipsum",
        "c3_raw": [2, 4, 6, 8],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": True,
        "c3_numbers_count": 4,
        "c3_numbers_has_even": True,
    }
    result = score_water_row("1", "r1", analysis)
    assert result["route"] == "Route B"
    assert result["score_achieved"] == 1
    assert result["maximum_score"] == 2

def test_score_water_row_zero_score():
    analysis = {
        "parsed_date": date(2024, 5, 15),
        "c2_raw": "2024-05-15",
        "c1": "lorem ipsum",
        "c3_raw": [11, 13, 15, 17],
        "statement_1_present": True,
        "statement_2_present": True,
        "statement_3_present": False,
        "c3_numbers_count": 4,
        "c3_numbers_has_even": False,
    }
    result = score_water_row("1", "r1", analysis)
    assert result["score_achieved"] == 0
    assert result["route"] == "Route A"
