# VEDA TASK 2

This repository contains VEDA TASK 2.

## Architecture Overview

This are the Phase wise details: 

1. **Phase 1: Shape Detection (`shape_detector.py`)** Analyzes the metadata and row structure to classify the data into one of 8 standardized shapes (e.g., `TREND`, `GROUPED_AGGREGATE`, `TOP_N`).
2. **Phase 2: Insight Extraction (`insight_extractor.py` & `deterministic_summary.py`)** Dynamically extracts mathematical facts (percentages, peaks, leaders) and safely converts them into a hardcoded, deterministic string.
3. **Phase 3: Narrative Layer & Validation (`narrative_layer.py` & `faithfulness_validator.py`)**
   Passes the deterministic text to an LLM (`Qwen2.5-1.5B-Instruct`) for polishing (with a strict 3.0s hard-timeout). The output is then passed through a rigorous mathematical validator. If the LLM hallucinates a single entity, fabricates a number, or fails a magnitude ratio check (e.g., "tripled"), the text is silently dropped, and the system falls back to the deterministic summary.
4. **Phase 4: Handoff & Edge Cases (`summarizer.py`)**
   The main engine wiring the pipeline together, fortified against 10k+ rows, null values, mixed types, and chaotic fuzzer inputs.

---

## Dynamic Column Inference

As Per the task, **no column names are hardcoded** in this pipeline. The system dynamically infers the roles of columns (Dimension vs. Measure) using the following fallback ways:

1. **Explicit Hints:** If the planner provides explicit `dimension` or `measure` keys in the `hints` dictionary, they are used immediately.
2. **Type Scanning:** The system scans the first row to categorize columns into `numeric_cols` (pure int/float) and `non_numeric_cols` (strings, dates, booleans).
3. **Measure Default:** Defaults to the **last** numeric column found (following standard SQL `SELECT ... SUM(x)` conventions). If no numeric columns exist, it defaults to the last column overall.
4. **Dimension Default:** Defaults to the **first** non-numeric column found (following standard SQL `GROUP BY` conventions). If all columns are numeric, it defaults to the first column overall.

---

## How to Run

### 1. Run the Demo
A live demonstration script is provided to print the end-to-end processing of all 8 standard shapes.

```bash
python demo.py

```

### 2. Run the Test Suite (with Fuzzing)

The test suite utilizes `pytest` to verify the deterministic logic, the exact string outputs, the hallucination validator, and edge cases. It includes a Fuzzer that bombards the main `summarize()` function with 100 iterations of random, chaotic data structures to prove the pipeline never crashes.

To run the tests and generate a coverage report:

```bash
python -m pytest tests/ -v --cov=.

```

## Design Decisions & Constraints

* **Strict Standard Library Usage:** No external dependencies (like Pandas or NumPy) were used for data manipulation. Only native Python dictionaries and lists. ****But**** for mock LLM `torch, transformers, AutoTokenizer, AutoModelForCausalLM` are called.
* **LLM Agnosticism & Local Testing:** The `narrative_layer` accepts any generic callable. For testing purposes, a mock/dummy LLM is utilized in the test suite to bypass network latency and PyTorch VRAM overhead, ensuring the fuzzer runs instantly.
* **Fail-Safe Fallbacks:** Every dictionary access is protected via `.get()`, and mixed-type edge cases are strictly filtered to ensure mathematical operations (like `max()` or `sorted()`) never raise type errors during execution.
