def render(shape: str, facts: dict) -> str:
    if shape == 'EMPTY':
        return "No results found for this query."
        
    if shape == 'COUNT':
        return f"There are {facts.get('total')} {facts.get('entity')} in total."
        
    if shape == 'GROUPED_AGGREGATE':
        top = facts.get('top', {})
        bottom = facts.get('bottom', {})
        return (f"Total is {facts.get('grand_total')} across {facts.get('n_groups')} groups. "
                f"{top.get('label')} is highest at {top.get('value')} ({top.get('pct')}%); "
                f"{bottom.get('label')} is lowest at {bottom.get('value')} ({bottom.get('pct')}%).")
                
    if shape == 'TREND':
        start = facts.get('start', {})
        end = facts.get('end', {})
        peak = facts.get('peak', {})
        low = facts.get('low', {})
        measure = str(facts.get('measure_name', 'value')).capitalize()
        return (f"{measure} {facts.get('direction')} {facts.get('pct_change')}% "
                f"from {start.get('label')} ({start.get('value')}) to {end.get('label')} ({end.get('value')}). "
                f"Peak was {peak.get('value')} ({peak.get('label')}); low was {low.get('value')} ({low.get('label')}).")
                
    if shape == 'COMPARISON':
        a = facts.get('a', {})
        b = facts.get('b', {})
        measure = str(facts.get('measure_name', 'value')).capitalize()
        return (f"{measure} is {facts.get('direction')} {facts.get('pct_change')}% "
                f"({a.get('value')} -> {b.get('value')}).")
                
    if shape == 'TOP_N':
        items = facts.get('items', [])
        leader = facts.get('leader', {})
        measure = str(facts.get('measure_name', 'total')).lower()
        item_strs = [f"{item['label']} ({item['value']})" for item in items]
        return (f"Top {len(items)} by {measure}: {', '.join(item_strs)}. "
                f"{leader.get('label')} leads with {leader.get('pct')}% of the top-{len(items)} total.")
                
    if shape == 'SINGLE_RECORD':
        fields = facts.get('fields', [])
        field_strs = [f"{k} = {v}" for k, v in fields]
        return f"1 record: {', '.join(field_strs)}."
        
    if shape == 'UNKNOWN':
        cols = facts.get('columns', [])
        n_rows = facts.get('n_rows', 0)
        return f"Query returned {n_rows} row with columns: {', '.join(cols)}."
        
    return "Summary could not be generated."