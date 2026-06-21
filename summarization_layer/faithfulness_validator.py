import re

MAGNITUDE_WORDS = {
    "doubled": 2.0,
    "tripled": 3.0,
    "quadrupled": 4.0,
    "halved": 0.5,
    "10x": 10.0
}

def get_allowed_numbers(rows: list[dict], facts: dict) -> set:
    nums = set()
        
    for r in rows:
        for v in r.values():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                nums.add(round(float(v), 1))
                
    def extract_dict(d):
        for v in d.values():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                nums.add(round(float(v), 1))
            elif isinstance(v, dict):
                extract_dict(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict): extract_dict(item)
                    elif isinstance(item, (int, float)) and not isinstance(item, bool):
                        nums.add(round(float(item), 1))
                        
    extract_dict(facts)
    return nums

def get_allowed_entities(rows: list[dict]) -> set:
    entities = set()
    for r in rows:
        for v in r.values():
            if isinstance(v, str):
                entities.add(v.lower())
    return entities

def validate(narrative: str, facts: dict, rows: list[dict]) -> bool:
    if not narrative: return False
    
    narrative_lower = narrative.lower()
    allowed_numbers = get_allowed_numbers(rows, facts)
    allowed_entities = get_allowed_entities(rows)
    
    for word, factor in MAGNITUDE_WORDS.items():
        # print('Ratio working')
        if word in narrative_lower:
            start = facts.get('start', {}).get('value')
            end = facts.get('end', {}).get('value')
            
            if start and end and start != 0:
                ratio = end / start
                if abs(ratio - factor) > 0.1: 
                    return False
            else:
                return False 
    
        
    clean_text = re.sub(r'[$,%]', '', narrative_lower)
    clean_text = re.sub(r'\b10x\b', '', clean_text) 
    
    found_numbers = [float(n) for n in re.findall(r'-?\d+(?:\.\d+)?', clean_text)]
    
    for num in found_numbers:
        # print('Number working')
        if not any(abs(num - allowed) <= 0.1 for allowed in allowed_numbers):
            return False
   

    sentences = re.split(r'[.!?]\s+', narrative)
    # print('Entities working')
    for sentence in sentences:
        words = sentence.split()
        if len(words) > 1:
            for word in words[1:]:
                clean_word = re.sub(r'[^a-zA-Z]', '', word)
                if clean_word.istitle() and len(clean_word) > 2:
                    if clean_word.lower() not in allowed_entities and clean_word.lower() not in ['total', 'peak', 'low', 'top']:
                        return False
    

    return True

# if __name__ == '__main__':
#     mock_rows = [
#         {"month": "Jan", "sales": 100}, 
#         {"month": "Mar", "sales": 180}
#     ]
#     mock_facts = {
#         "start": {"value": 100}, 
#         "end": {"value": 180}, 
#         "pct_change": 80.0
#     }

    # good_narrative = "Sales went from 100 to 180, an 80.0% increase."
    # result_good = validate(good_narrative, mock_facts, mock_rows)
    # print('True') if result_good else print('Fail')

    # bad_number_narrative = "Sales went from 100 to 180, which is an 85.0% increase."
    # result_bad_num = validate(bad_number_narrative, mock_facts, mock_rows)
    # print('True') if not result_bad_num else print('Fail')

    # bad_magnitude_narrative = "Sales nearly tripled from Jan to Mar."
    # result_bad_mag = validate(bad_magnitude_narrative, mock_facts, mock_rows)
    # print('True') if not result_bad_mag else print('Fail')