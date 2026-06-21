import pytest
from faithfulness_validator import validate

@pytest.fixture
def trend_data():
    return {
        "rows": [{"month": "Jan", "sales": 100}, {"month": "Mar", "sales": 180}],
        "facts": {"start": {"value": 100}, "end": {"value": 180}, "pct_change": 80.0}
    }

def test_validator_pass_case(trend_data):
    narrative = "Sales went from 100 to 180, an 80.0% increase."
    assert validate(narrative, trend_data["facts"], trend_data["rows"]) is True

def test_validator_wrong_number(trend_data):
    narrative = "Sales went from 100 to 180, which is an 85.0% increase." 
    assert validate(narrative, trend_data["facts"], trend_data["rows"]) is False

def test_validator_hallucinated_entity(trend_data):
    narrative = "Sales in London went from 100 to 180."
    assert validate(narrative, trend_data["facts"], trend_data["rows"]) is False

def test_validator_tripled(trend_data):
    narrative = "Sales nearly tripled from Jan to Mar."
    assert validate(narrative, trend_data["facts"], trend_data["rows"]) is False

def test_validator_pct_within_tolerance(trend_data):
    narrative = "Sales increased by 80.08%."
    assert validate(narrative, trend_data["facts"], trend_data["rows"]) is True