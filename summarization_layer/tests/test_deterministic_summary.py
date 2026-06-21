import pytest
from deterministic_summary import render

def test_render_empty():
    assert render('EMPTY', {}) == "No results found for this query."

def test_render_count():
    facts = {"total": 759, "entity": "orders"}
    assert render('COUNT', facts) == "There are 759 orders in total."

def test_render_grouped_aggregate():
    facts = {
        "grand_total": 968,
        "n_groups": 2,
        "top": {"label": "Approved", "value": 759, "pct": 78.4},
        "bottom": {"label": "Rejected", "value": 209, "pct": 21.6}
    }
    expected = "Total is 968 across 2 groups. Approved is highest at 759 (78.4%); Rejected is lowest at 209 (21.6%)."
    assert render('GROUPED_AGGREGATE', facts) == expected

def test_render_trend():
    facts = {
        "start": {"label": "Jan", "value": 100},
        "end": {"label": "Mar", "value": 180},
        "pct_change": 80.0,
        "direction": "rose",
        "peak": {"label": "Mar", "value": 180},
        "low": {"label": "Jan", "value": 100},
        "measure_name": "sales"
    }
    expected = "Sales rose 80.0% from Jan (100) to Mar (180). Peak was 180 (Mar); low was 100 (Jan)."
    assert render('TREND', facts) == expected

def test_render_comparison():
    facts = {
        "a": {"label": "2022", "value": 1000},
        "b": {"label": "2023", "value": 1250},
        "pct_change": 25.0,
        "direction": "up",
        "measure_name": "revenue"
    }
    expected = "Revenue is up 25.0% (1000 -> 1250)."
    assert render('COMPARISON', facts) == expected

def test_render_top_n():
    facts = {
        "items": [
            {"label": "Alice", "value": 500, "pct": 62.5},
            {"label": "Bob", "value": 300, "pct": 37.5}
        ],
        "leader": {"label": "Alice", "value": 500, "pct": 62.5},
        "measure_name": "Points"
    }
    expected = "Top 2 by points: Alice (500), Bob (300). Alice leads with 62.5% of the top-2 total."
    assert render('TOP_N', facts) == expected

def test_render_single_record():
    facts = {
        "fields": [("id", 101), ("status", "Active"), ("priority", "High")]
    }
    expected = "1 record: id = 101, status = Active, priority = High."
    assert render('SINGLE_RECORD', facts) == expected

def test_render_unknown():
    facts = {
        "n_rows": 5,
        "columns": ["id", "name", "timestamp"]
    }
    expected = "Query returned 5 row with columns: id, name, timestamp."
    assert render('UNKNOWN', facts) == expected

def test_render_fallback():
    assert render('SOMETHING_ELSE', {}) == "Summary could not be generated."