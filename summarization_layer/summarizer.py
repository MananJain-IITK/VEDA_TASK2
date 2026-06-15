from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class SummaryResult:
    shape: str                    # COUNT | GROUPED_AGGREGATE | TREND | COMPARISON | TOP_N | SINGLE_RECORD | EMPTY | UNKNOWN
    insights: List[str]           # human-readable key facts, one per line
    facts: Dict                   # raw extracted facts (numbers + labels) testable
    deterministic_summary: str    # ALWAYS present, ALWAYS correct
    narrative_summary: Optional[str] # polished text; None if LLM unavailable or failed
    validated: bool               # did narrative pass faithfulness check
    fallback_used: bool           # True if narrative is None or failed validation

