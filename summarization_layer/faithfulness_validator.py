import re

def get_allowed_numbers(facts: dict) -> set:
    allowed = set()
    def extract(obj):
        if isinstance(obj, (int, float)) and not isinstance(obj, bool):
            allowed.add(round(float(obj), 1))
        elif isinstance(obj, dict):
            for v in obj.values(): extract(v)
        elif isinstance(obj, list):
            for item in obj: extract(item)
    extract(facts)
    return allowed

def get_allowed_entities(facts: dict) -> set:
    allowed = set()
    def extract(obj):
        if isinstance(obj, str):
            allowed.add(obj.lower())
        elif isinstance(obj, dict):
            for v in obj.values(): extract(v)
        elif isinstance(obj, list):
            for item in obj: extract(item)
    extract(facts)
    return allowed

def validate(narrative: str, facts: dict, rows: list, shape: str, det_summary: str) -> bool:
    if not narrative:
        return False

    allowed_numbers = get_allowed_numbers(facts)
    words = narrative.split()
    for word in words:
        clean_num = re.sub(r'[^\d.]', '', word)
        if clean_num:
            try:
                num_val = round(float(clean_num), 1)
                if not any(abs(num_val - a) <= 0.10 for a in allowed_numbers):
                    return False
            except ValueError:
                continue

    narrative_lower = narrative.lower()
    multipliers = {"doubled": 2.0, "tripled": 3.0, "halved": 0.5}
    found_mult = None
    
    for word, mult in multipliers.items():
        if word in narrative_lower:
            found_mult = mult
            break
            
    if found_mult:
        expected_ratio = None

        if shape == 'TREND' and 'start' in facts and 'end' in facts:
            start_val = facts['start'].get('value', 0)
            end_val = facts['end'].get('value', 0)
            if start_val != 0: expected_ratio = end_val / start_val
                
        elif shape == 'COMPARISON' and 'a' in facts and 'b' in facts:
            a_val = facts['a'].get('value', 0)
            b_val = facts['b'].get('value', 0)
            if a_val != 0: expected_ratio = b_val / a_val

        if expected_ratio is not None:
            if abs(expected_ratio - found_mult) > 0.10:
                return False
            
    safe_vocab = set(re.findall(r'[a-z]+', det_summary.lower()))
    safe_vocab.update(get_allowed_entities(facts))
    
    dashboard_grammar = {
        "rose", "fell", "up", "down", "increased", "decreased", "dropped", "jumped",
        "tripled", "doubled", "halved", "by", "of", "to", "from", "at", "in", "is", 
        "was", "are", "were", "has", "had", "total", "peak", "low", "top", "bottom", 
        "records", "group", "groups", "across", "highest", "lowest", "points", "leads", 
        "with", "the", "a", "an", "and", "but", "or", "for", "overall", "about", 
        "approximately", "nearly", "almost", "record", "fields", "query", "returned", 
        "columns", "row", "rows", "sales", "revenue", "orders", "count", "value",
        "percent", "pct", "change", "over", "time", "between", "than", "more", "less"
    }
    safe_vocab.update(dashboard_grammar)
    narrative_words = set(re.findall(r'[a-z]+', narrative_lower))
    
    for word in narrative_words:
        if word not in safe_vocab:
            return False

    return True