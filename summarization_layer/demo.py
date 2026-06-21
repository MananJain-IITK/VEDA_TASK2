from summarizer import summarize
from fixtures.test_fixtures import STANDARD_FIXTURES

def run_demo():
    print("Running VEDA")
    for shape_name, fixture in STANDARD_FIXTURES.items():
        print(f"\n[{shape_name.upper()}]")
        print(f"Rows : {fixture['rows']}")
        print(f"Hints: {fixture.get('hints', {})}")
        
        result = summarize(
            query=f"testing {shape_name}",
            rows=fixture["rows"],
            hints=fixture.get("hints", {}),
            mock_llm=None
        )
        print(f"Detected Shape  : {result.shape}")
        print(f"Facts Extracted : {result.facts}")
        print(f"Deterministic   : {result.deterministic_summary}")
        if result.narrative_summary:
            print(f"LLM Narrative   : {result.narrative_summary}")
            print(f"Passed Validator: {result.validated}")
        else:
            print(f"Fallback Used   : True (Narrative bypassed or failed validation)")

if __name__ == "__main__":
    run_demo()