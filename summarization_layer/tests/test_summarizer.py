import pytest
import random
import string
from summarizer import summarize
from fixtures.test_fixtures import STANDARD_FIXTURES, EDGE_FIXTURES

@pytest.mark.parametrize("shape_name", STANDARD_FIXTURES.keys())
def test_summarize_all_standard_shapes(shape_name):
    fixture = STANDARD_FIXTURES[shape_name]
    result = summarize(f"show me {shape_name}", fixture["rows"], fixture.get("hints", {}))
    assert isinstance(result.deterministic_summary, str)
    assert result.deterministic_summary != "Summary could not be generated."

@pytest.mark.parametrize("fixture_name", EDGE_FIXTURES.keys())
def test_summarize_edge_cases(fixture_name):
    fixture = EDGE_FIXTURES[fixture_name]
    result = summarize("edge case query", fixture["rows"], fixture.get("hints", {}))
    assert result.deterministic_summary is not None

def test_summarize_fuzzer_never_raises():
    intents = ["count", "grouped", "trend", "comparison", "top_n", "single", None, "garbage_intent"]
    
    for i in range(100):
        rows = []
        for j in range(random.randint(0, 50)):
            row = {}
            for k in range(random.randint(0, 5)):
                col_name = ''.join(random.choices(string.ascii_letters, k=5))
                val_type = random.choice(['int', 'float', 'str', 'none', 'unicode'])
                
                if val_type == 'int': val = random.randint(-1000, 1000)
                elif val_type == 'float': val = random.random() * 100
                elif val_type == 'str': val = ''.join(random.choices(string.ascii_letters, k=5))
                elif val_type == 'none': val = None
                else: val = "测试" # Unicode
                
                row[col_name] = val
            rows.append(row)
            
        hints = {"intent": random.choice(intents)}
        try:
            result = summarize("random query", rows, hints)
            assert result is not None
        except Exception as e:
            pytest.fail(f"summarize() raised an exception during fuzzing! Error: {e}\nHints: {hints}\nRows: {rows[:2]}")