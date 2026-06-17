import pytest
from insight_extractor import extract
from fixtures.test_fixtures import STANDARD_FIXTURES

def test_extract_count():
    fixture = STANDARD_FIXTURES["count"]
    facts = extract(fixture["rows"], "COUNT", fixture["hints"])
    assert facts["total"] == 759
    assert facts["entity"] == "orders"

def test_extract_grouped_aggregate():
    fixture = STANDARD_FIXTURES["grouped"]
    facts = extract(fixture["rows"], "GROUPED_AGGREGATE", fixture["hints"])
    assert facts["grand_total"] == 968
    assert facts["n_groups"] == 2
    assert facts["top"]["label"] == "Approved"
    assert facts["top"]["pct"] == 78.4 
    assert facts["bottom"]["label"] == "Rejected"
    assert facts["bottom"]["pct"] == 21.6

def test_extract_trend():
    fixture = STANDARD_FIXTURES["trend"]
    facts = extract(fixture["rows"], "TREND", fixture["hints"])
    assert facts["start"]["value"] == 100
    assert facts["end"]["value"] == 180
    assert facts["pct_change"] == 80.0
    assert facts["direction"] == "rose"
    assert facts["peak"]["value"] == 180
    assert facts["low"]["value"] == 100

def test_extract_comparison():
    fixture = STANDARD_FIXTURES["comparison"]
    facts = extract(fixture["rows"], "COMPARISON", fixture["hints"])
    assert facts["a"]["value"] == 100
    assert facts["b"]["value"] == 112
    assert facts["pct_change"] == 12.0
    assert facts["direction"] == "up"

def test_extract_top_n():
    fixture = STANDARD_FIXTURES["top_n"]
    facts = extract(fixture["rows"], "TOP_N", fixture["hints"])
    assert len(facts["items"]) == 3
    assert facts["leader"]["label"] == "A"
    assert facts["leader"]["value"] == 50
    assert facts["leader"]["pct"] == 50.0 

def test_extract_handles_zero_division():
    """Edge case: ensuring totals of 0 don't crash the percentage calculations."""
    rows = [{"name": "A", "val": 0}, {"name": "B", "val": 0}]
    facts = extract(rows, "GROUPED_AGGREGATE", {"intent": "grouped"})
    assert facts["grand_total"] == 0
    assert facts["top"]["pct"] == 0.0