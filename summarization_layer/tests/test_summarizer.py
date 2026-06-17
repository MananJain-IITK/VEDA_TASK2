import pytest
from summarizer import summarize
from fixtures.test_fixtures import STANDARD_FIXTURES

def test_summarize_count_e2e():
    fixture = STANDARD_FIXTURES["count"]
    result = summarize("how many orders?", fixture["rows"], fixture["hints"])
    assert result.shape == "COUNT"
    assert result.deterministic_summary == "There are 759 orders in total."
    assert result.fallback_used is True

def test_summarize_trend_e2e():
    fixture = STANDARD_FIXTURES["trend"]
    result = summarize("sales over time", fixture["rows"], fixture["hints"])
    assert result.shape == "TREND"
    assert result.deterministic_summary == "Sales rose 80.0% from Jan (100) to Mar (180). Peak was 180 (Mar); low was 100 (Jan)."

def test_summarize_grouped_e2e():
    fixture = STANDARD_FIXTURES["grouped"]
    result = summarize("sales by status", fixture["rows"], fixture["hints"])
    assert result.shape == "GROUPED_AGGREGATE"
    assert result.deterministic_summary == "Total is 968 across 2 groups. Approved is highest at 759 (78.4%); Rejected is lowest at 209 (21.6%)."

def test_summarize_empty_e2e():
    fixture = STANDARD_FIXTURES["empty"]
    result = summarize("show me nothing", fixture["rows"], fixture["hints"])
    assert result.shape == "EMPTY"
    assert result.deterministic_summary == "No results found for this query."