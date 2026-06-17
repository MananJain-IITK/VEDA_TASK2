import pytest
from shape_detector import detect_shape
from fixtures.test_fixtures import STANDARD_FIXTURES, EDGE_FIXTURES

@pytest.mark.parametrize("fixture_name, expected_shape", [
    ("count", "COUNT"),
    ("grouped", "GROUPED_AGGREGATE"),
    ("trend", "TREND"),
    ("comparison", "COMPARISON"),
    ("top_n", "TOP_N"),
    ("single", "SINGLE_RECORD"),
    ("empty", "EMPTY"),
    ("unknown", "UNKNOWN"),
])
def test_detect_shape_standard_fixtures(fixture_name, expected_shape):
    fixture = STANDARD_FIXTURES[fixture_name]
    assert detect_shape(fixture["rows"], fixture["hints"]) == expected_shape

@pytest.mark.parametrize("fixture_name, expected_shape", [
    ("empty_with_hint", "TREND"),
    ("single_group_grouped", "GROUPED_AGGREGATE"),
    ("tie_top_bottom", "TOP_N"),
    ("negative_values", "TREND"),
])
def test_detect_shape_edge_fixtures(fixture_name, expected_shape):
    fixture = EDGE_FIXTURES[fixture_name]
    assert detect_shape(fixture["rows"], fixture["hints"]) == expected_shape


def test_shape_inference_without_hints():
    assert detect_shape([{"val": 50}], {}) == "COUNT"
    assert detect_shape([{"id": 1, "name": "foo"}], {}) == "UNKNOWN"
    assert detect_shape([{"status": "A", "val": 10}, {"status": "B", "val": 20}], {}) == "GROUPED_AGGREGATE"
    assert detect_shape([{"col1": "A", "col2": "B"}], {}) == "UNKNOWN"