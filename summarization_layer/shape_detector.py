def _is_number(val) -> bool:
    return isinstance(val, (int, float)) and not isinstance(val, bool)

def _only_value(row: dict):
    return list(row.values())[0] if row else None

def _has_one_dimension_and_one_measure(rows: list[dict]) -> bool:
    if not rows or len(rows[0]) != 2:
        return False
    
    vals = list(rows[0].values())
    return (_is_number(vals[0]) and not _is_number(vals[1])) or \
           (not _is_number(vals[0]) and _is_number(vals[1]))


def detect_shape(rows: list[dict], hints: dict) -> str:
    # Priority 1: Trust planner hints
    intent = str(hints.get('intent', '')).lower()
    
    if intent == 'count': return 'COUNT'
    if intent == 'trend': return 'TREND'
    if intent in ('grouped', 'group_by'): return 'GROUPED_AGGREGATE'
    if intent == 'comparison': return 'COMPARISON'
    if intent == 'top_n': return 'TOP_N'
    if intent == 'single': return 'SINGLE_RECORD'
    
    # Priority 2: Infer from row structure
    if not rows:
        return 'EMPTY'
    
    if len(rows) == 1 and len(rows[0]) == 1:
        if _is_number(_only_value(rows[0])):
            return 'COUNT'
            
    if _has_one_dimension_and_one_measure(rows):
        return 'GROUPED_AGGREGATE'
        
    # Priority 3: Safe fallback, never guess
    return 'UNKNOWN'