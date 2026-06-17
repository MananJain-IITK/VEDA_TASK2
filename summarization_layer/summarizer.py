from dataclasses import dataclass
from typing import List, Dict, Optional
from shape_detector import detect_shape
from insight_extractor import extract
from deterministic_summary import render

@dataclass
class SummaryResult:
    shape: str                    # COUNT | GROUPED_AGGREGATE | TREND | COMPARISON | TOP_N | SINGLE_RECORD | EMPTY | UNKNOWN
    insights: List[str]           # human-readable key facts, one per line
    facts: Dict                   # raw extracted facts (numbers + labels) testable
    deterministic_summary: str    # ALWAYS present, ALWAYS correct
    narrative_summary: Optional[str] # polished text; None if LLM unavailable or failed
    validated: bool               # did narrative pass faithfulness check
    fallback_used: bool           # True if narrative is None or failed validation

def summarize(query: str, rows: List[dict], hints: dict) -> SummaryResult:
    shape = detect_shape(rows, hints)
    facts = extract(rows, shape, hints)
    det_summary = render(shape, facts)
    narrative = None
    validated = False
    fallback = True 
    
    return SummaryResult(
        shape=shape,
        insights=[], 
        facts=facts,
        deterministic_summary=det_summary,
        narrative_summary=narrative,
        validated=validated,
        fallback_used=fallback
    )