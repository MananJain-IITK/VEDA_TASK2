import time
import statistics
import requests
from fixtures.test_fixtures import STANDARD_FIXTURES
from shape_detector import detect_shape
from insight_extractor import extract
from deterministic_summary import render
from faithfulness_validator import validate

OLLAMA_URL = "http://localhost:11434/api/generate"
MODELS = [
    "qwen2.5:0.5b", "llama3.2:1b", "qwen2.5:1.5b-instruct", 
    "gemma2:2b", "smollm2:1.7b", "llama3.2:3b", 
    "phi3:mini", "qwen2.5:3b", "mistral:7b"
]
SHAPES = ["count", "grouped", "trend", "comparison", "top_n", "single"]
N_CALLS = 20

def benchmark_models():
    print(f" Target: {N_CALLS} runs per shape across {len(SHAPES)} shapes.")

    for model in MODELS:
        print(f"\nBenchmarking {model}")
        latencies = []
        passed_validation = 0
        under_3s = 0
        total_runs = 0

        for shape_name in SHAPES:
            fixture = STANDARD_FIXTURES[shape_name]
            rows = fixture["rows"]
            hints = fixture.get("hints", {})
            shape = detect_shape(rows, hints)
            facts = extract(rows, shape, hints)
            det_summary = render(shape, facts)

            prompt = (
                "You are a strict data-to-text editor for a corporate dashboard. "
                "Rewrite the provided summary to sound slightly more natural. "
                "CRITICAL RULES: \n"
                "1. NEVER add, change, or invent any number, name, or fact.\n"
                "2. Keep the output extremely concise.\n"
                "3. Do not include introductory or conversational filler text.\n"
                f"Raw Facts: {facts}\n"
                f"Original Summary: {det_summary}\n\n"
                f"Polished Summary:"
            )

            for i in range(N_CALLS):
                total_runs += 1
                start = time.time()
                
                try:
                    resp = requests.post(OLLAMA_URL, json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.1}
                    }, timeout=15.0)
                    
                    latency = time.time() - start
                    latencies.append(latency)
                    
                    if latency <= 3.0:
                        under_3s += 1
                        
                    if resp.status_code == 200:
                        narrative = resp.json().get("response", "").strip()
                        
                        is_valid = validate(narrative, facts, rows, shape, det_summary)
                        if is_valid:
                            passed_validation += 1
                            
                except requests.exceptions.RequestException:
                    latencies.append(15.0) 
        
        if not latencies:
            print("Failed to connect to model.")
            continue

        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies)
        
        print(f"  Total Runs         : {total_runs}")
        print(f"  p50 Latency        : {p50:.2f}s")
        print(f"  p95 Latency        : {p95:.2f}s")
        print(f"  Within 3s Cap      : {(under_3s / total_runs) * 100:.1f}%")
        print(f"  Validator Pass Rate: {(passed_validation / total_runs) * 100:.1f}%")

if __name__ == "__main__":
    benchmark_models()
