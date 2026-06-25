# VEDA TASK 2

This repository contains the completed data-to-text pipeline for VEDA TASK 2.

## Architecture Overview

This pipeline is built in four distinct phases: 

1. **Phase 1: Shape Detection (`shape_detector.py`)** Analyzes the metadata and row structure to classify the data into one of 8 standardized shapes (e.g., `TREND`, `GROUPED_AGGREGATE`, `TOP_N`). Empty datasets instantly resolve to `EMPTY`.
2. **Phase 2: Insight Extraction (`insight_extractor.py` & `deterministic_summary.py`)** Dynamically extracts mathematical facts (percentages, peaks, leaders) and safely converts them into a hardcoded, deterministic string aligned with the product spec.
3. **Phase 3: Narrative Layer & Validation (`narrative_layer.py` & `faithfulness_validator.py`)**
   Passes the deterministic text to an SLM for natural polishing. The output is then passed through a rigorous mathematical validator. The validator utilizes shape-aware magnitude checks (e.g., branching math for "doubled") and a strict tokenized Safe Vocabulary whitelist. If the LLM hallucinates a single entity or fabricates a number, the text is silently dropped, and the system falls back to the deterministic summary.
4. **Phase 4: Handoff & Edge Cases (`summarizer.py`)**
   The main engine wiring the pipeline together, fortified against 10k+ rows, null values, mixed types, and chaotic fuzzer inputs.

---

## Dynamic Column Inference

As per the task, **no column names are hardcoded** in this pipeline. The system dynamically infers the roles of columns (Dimension vs. Measure) using the following fallback cascade:

1. **Explicit Hints:** If the planner provides explicit `dimension` or `measure` keys in the `hints` dictionary, they are used immediately.
2. **Type Scanning:** The system scans the first row to categorize columns into `numeric_cols` (pure int/float) and `non_numeric_cols` (strings, dates, booleans).
3. **Measure Default:** Defaults to the **last** numeric column found (following standard SQL `SELECT ... SUM(x)` conventions). If no numeric columns exist, it defaults to the last column overall.
4. **Dimension Default:** Defaults to the **first** non-numeric column found (following standard SQL `GROUP BY` conventions). If all columns are numeric, it defaults to the first column overall.

---

## The Facts Dictionary Contract

To ensure strict alignment between the extraction, rendering, and validation layers, the `facts` dictionary acts as the single source of truth. Mathematical outputs are strictly enforced. 
* **Derived Counts:** Shapes like `TOP_N` and `SINGLE_RECORD` dynamically inject their derived counts (`"n"` and `"record_count"`) into the facts dictionary so the validator can seamlessly authorize those numbers.
* **Measure Names:** Shapes that track specific metrics (`TREND`, `COMPARISON`, `TOP_N`) include a `measure_name` key. This allows the deterministic templates to dynamically state what is being measured (e.g., "Revenue is up..." instead of defaulting to "Total is up...").

---

## Known Spec Deviations: Single-Row Behavior

As requested by the specification, any intentional deviations are documented here. 

**Deviation:** If a query returns exactly one row but contains multiple columns of unaggregated data, the Shape Detector currently classifies it as `UNKNOWN` instead of `SINGLE_RECORD`.

**Rationale:** A single multi-column row without an explicit `intent` hint is mathematically indistinguishable from a standard unaggregated table that just happens to only have one entry. Rather than making a presumptive leap that the user wants a "Detail View" layout, the pipeline defaults to the safer, metadata-driven `UNKNOWN` state (e.g., "Query returned 1 row with columns..."). This ensures we don't force a single-record UI layout unless explicitly instructed by upstream hints.

---

## Benchmark results
### 1. benchmark_results
This results are for the system prompt:
```bash
prompt = (
 "You are a strict data-to-text editor for a corporate dashboard. "
 "Rewrite the provided summary to sound slightly more natural. "
 "CRITICAL RULES: \n"
 "1. NEVER add, change, or invent any number, name, or fact.\n"
 "2. Keep the output extremely concise.\n"
 f"Raw Facts: {facts}\n"
 f"Original Summary: {det_summary}\n\n"
 f"Polished Summary:"
)
```
### 2. benchmark_results1
This results are for the system prompt:
```bash
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
```

### Verdict
`benchmark_result1` showed better performance as compared to `benchmark_result` in terms of speed and validator pass. The reason is that the third line in the second prompt is preventing any unnecessary filler words which is the reason it is passing the validator.

---

## How to Run

### 1. Run the Demo
A live demonstration script is provided to print the end-to-end processing of all standard shapes.

```bash
python demo.py

```

### 2. Run the Test Suite (with Fuzzing)

The test suite utilizes `pytest` to verify the deterministic logic, the exact string outputs, the hallucination validator, and edge cases. It includes a Fuzzer that bombards the main `summarize()` function with 100 iterations of random, chaotic data structures to prove the pipeline never crashes.

```bash
python -m pytest tests/ -v --cov=.

```

### 3. Run the SLM Benchmarking Protocol

A dedicated `benchmark.py` script is included to test local SLMs via Ollama, tracking p50/p95 latency, SLA caps, and validator pass rates. Ensure the Ollama server is running and your target models are pulled before executing.

```bash
ollama serve
ollama pull qwen2.5:1.5b-instruct
python benchmark.py > benchmark_results.txt

```

---

## Design Decisions & Constraints

* **Strict Standard Library Usage:** No external dependencies (like Pandas or NumPy) were used for core data manipulation. Only native Python dictionaries and lists to ensure zero-bloat execution.
* **LLM Agnosticism & Local Testing:** The `narrative_layer` accepts any generic callable. For rapid unit testing, a mock SLM is utilized to bypass network latency and VRAM overhead, ensuring the fuzzer runs instantly. Live SLA benchmarking is deferred to `benchmark.py` via local Ollama HTTP requests.
* **Fail-Safe Fallbacks:** Every dictionary access is protected via `.get()`, and mixed-type edge cases are strictly filtered to ensure mathematical operations (like `max()` or `sorted()`) never raise type errors during execution.
