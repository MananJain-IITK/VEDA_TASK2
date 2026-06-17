def _infer_columns(rows: list[dict], hints: dict) -> tuple:
    if not rows: return None, None
    
    measure_col = hints.get("measure")
    dimension_col = hints.get("dimension") 
    
    if measure_col and dimension_col:
        return dimension_col, measure_col
        
    cols = list(rows[0].keys())
    numeric_cols = [c for c in cols if all(isinstance(r.get(c), (int, float)) and not isinstance(r.get(c), bool) for r in rows if r.get(c) is not None)]
    non_numeric_cols = [c for c in cols if c not in numeric_cols]
    
    if not measure_col:
        measure_col = numeric_cols[-1] if numeric_cols else cols[-1]
    
    if not dimension_col:
        dimension_col = non_numeric_cols[0] if non_numeric_cols else cols[0] 
        
    return dimension_col, measure_col

def extract(rows: list[dict], shape: str, hints: dict) -> dict:
    if shape == 'EMPTY' or not rows:
        return {} 
        
    if shape == 'COUNT':
        val = list(rows[0].values())[0] if rows else 0
        return {"total": val, "entity": hints.get("entity", "records")} 
        
    if shape == 'SINGLE_RECORD':
        return {"fields": [(k, v) for k, v in rows[0].items()]} 
        
    if shape == 'UNKNOWN':
        return {"n_rows": len(rows), "columns": list(rows[0].keys()) if rows else []} 

    dim, meas = _infer_columns(rows, hints)
    
    if shape == 'GROUPED_AGGREGATE':
        valid_rows = [r for r in rows if r.get(meas) is not None]
        sorted_rows = sorted(valid_rows, key=lambda x: x[meas], reverse=True)
        total = sum(r[meas] for r in valid_rows)
        
        def _get_pct(val, t): return round((val / t) * 100, 1) if t else 0.0
        
        top = sorted_rows[0] if sorted_rows else {dim: "N/A", meas: 0}
        bottom = sorted_rows[-1] if sorted_rows else {dim: "N/A", meas: 0}
        
        return {
            "grand_total": total,
            "n_groups": len(valid_rows),
            "top": {"label": top[dim], "value": top[meas], "pct": _get_pct(top[meas], total)},
            "bottom": {"label": bottom[dim], "value": bottom[meas], "pct": _get_pct(bottom[meas], total)},
            "items": sorted_rows
        } 
    if shape == 'TREND':
        valid_rows = [r for r in rows if r.get(meas) is not None]
        if not valid_rows: return {}
        start = valid_rows[0]
        end = valid_rows[-1]
        
        peak = max(valid_rows, key=lambda x: x[meas])
        low = min(valid_rows, key=lambda x: x[meas])
        
        start_val = start[meas]
        end_val = end[meas]
        pct_change = round(((end_val - start_val) / abs(start_val)) * 100, 1) if start_val else 0.0
        
        return {
            "start": {"label": start[dim], "value": start_val},
            "end": {"label": end[dim], "value": end_val},
            "pct_change": abs(pct_change),
            "direction": "rose" if end_val >= start_val else "fell",
            "peak": {"label": peak[dim], "value": peak[meas]},
            "low": {"label": low[dim], "value": low[meas]}
        } 

    if shape == 'COMPARISON':
        if len(rows) < 2: return {}
        a, b = rows[0], rows[1]
        a_val, b_val = a[meas], b[meas]
        pct_change = round(((b_val - a_val) / abs(a_val)) * 100, 1) if a_val else 0.0
        return {
            "a": {"label": a[dim], "value": a_val},
            "b": {"label": b[dim], "value": b_val},
            "pct_change": abs(pct_change),
            "direction": "up" if b_val >= a_val else "down"
        } 
        
    if shape == 'TOP_N':
        valid_rows = sorted([r for r in rows if r.get(meas) is not None], key=lambda x: x[meas], reverse=True)
        total = sum(r[meas] for r in valid_rows)
        def _get_pct(val, t): return round((val / t) * 100, 1) if t else 0.0
        
        items = [{"label": r[dim], "value": r[meas], "pct": _get_pct(r[meas], total)} for r in valid_rows]
        leader = items[0] if items else {"label": "N/A", "value": 0, "pct": 0.0}
        
        return {
            "items": items,
            "leader": leader
        } 

    return {}