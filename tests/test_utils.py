"""Tests for the DSSA assessment utilities."""

from src.utils import load_data


def test_load_data_returns_dict():
    """load_data should return a dict."""
    data = load_data()
    assert isinstance(data, dict)
