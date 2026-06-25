def render(shape: str, facts: dict) -> str:
    if shape == 'EMPTY':
        return "No results found for this query."
        
    if shape == 'COUNT':
        return f"There are {facts.get('total')} {facts.get('entity')} in total."
        
    if shape == 'GROUPED_AGGREGATE':
        total = facts.get('grand_total', 0)
        n_groups = facts.get('n_groups', 0)
        top = facts.get('top', {})
        bottom = facts.get('bottom', {})
        
        group_word = "group" if n_groups == 1 else "groups"
        
        return (f"Total is {total} across {n_groups} {group_word}. "
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
        pct = facts.get('pct_change', 0.0)
        direction = facts.get('direction', 'changed')
        measure = str(facts.get('measure_name', 'total')).capitalize()
        return f"{measure} is {direction} {pct}% ({a.get('value')} → {b.get('value')})."
                
    if shape == 'TOP_N':
        items = facts.get('items', [])
        leader = facts.get('leader', {})
        n = facts.get('n', len(items))
        measure = str(facts.get('measure_name', 'total')).lower()
        item_strs = [f"{item['label']} ({item['value']})" for item in items]
        return (f"Top {n} by {measure}: {', '.join(item_strs)}. "
                f"{leader.get('label')} leads with {leader.get('pct')}% of the top-{n} total.")
    
    if shape == 'SINGLE_RECORD':
        fields = facts.get('fields', [])
        record_count = facts.get('record_count', 1)
        field_strs = [f"{k}={v}" for k, v in fields] 
        return f"{record_count} record: {', '.join(field_strs)}."
        
    if shape == 'UNKNOWN':
        n = facts.get('n_rows', 0)
        cols = facts.get('columns', [])
        row_word = "row" if n == 1 else "rows"
        
        return f"Query returned {n} {row_word} with columns: {', '.join(cols)}."
        
    return "Summary could not be generated."