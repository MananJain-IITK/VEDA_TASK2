def infer_columns(rows: list[dict], hints: dict) -> tuple:
    if not rows: return None, None
    
    measure_col = hints.get("measure")
    dimension_col = hints.get("dimension") 
    
    if measure_col and dimension_col:
        return dimension_col, measure_col
        
    cols = list(rows[0].keys())
    if not cols:
        return None, None
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
        val = list(rows[0].values())[0] if rows and rows[0] else 0
        return {"total": val, "entity": hints.get("entity", "records")}
        
    if shape == 'SINGLE_RECORD':
        return {
            "record_count": 1, 
            "fields": [(k, v) for k, v in rows[0].items()]
        }
        
    if shape == 'UNKNOWN':
        return {"n_rows": len(rows), "columns": list(rows[0].keys()) if rows else []}

    dim, meas = infer_columns(rows, hints)
    
    if shape == 'GROUPED_AGGREGATE':
        valid_rows = [r for r in rows if isinstance(r.get(meas), (int, float)) and not isinstance(r.get(meas), bool)]
        sorted_rows = sorted(valid_rows, key=lambda x: x.get(meas, 0), reverse=True)
        total = sum(r.get(meas, 0) for r in valid_rows)
        
        def get_pct(val, t): return round((val / t) * 100, 1) if t else 0.0
        
        top = sorted_rows[0] if sorted_rows else {dim: "N/A", meas: 0}
        bottom = sorted_rows[-1] if sorted_rows else {dim: "N/A", meas: 0}
        
        return {
            "grand_total": total,
            "n_groups": len(valid_rows),
            "top": {"label": top.get(dim, "N/A"), "value": top.get(meas, 0), "pct": get_pct(top.get(meas, 0), total)},
            "bottom": {"label": bottom.get(dim, "N/A"), "value": bottom.get(meas, 0), "pct": get_pct(bottom.get(meas, 0), total)},
            "items": sorted_rows
        }

    if shape == 'TREND':
        valid_rows = [r for r in rows if isinstance(r.get(meas), (int, float)) and not isinstance(r.get(meas), bool)]
        if not valid_rows: return {}
        start = valid_rows[0]
        end = valid_rows[-1]
        
        peak = max(valid_rows, key=lambda x: x.get(meas, 0))
        low = min(valid_rows, key=lambda x: x.get(meas, 0))
        
        start_val = start.get(meas, 0)
        end_val = end.get(meas, 0)
        pct_change = round(((end_val - start_val) / abs(start_val)) * 100, 1) if start_val else 0.0
        
        return {
            "start": {"label": start.get(dim, "N/A"), "value": start_val},
            "end": {"label": end.get(dim, "N/A"), "value": end_val},
            "pct_change": abs(pct_change),
            "direction": "rose" if end_val >= start_val else "fell",
            "peak": {"label": peak.get(dim, "N/A"), "value": peak.get(meas, 0)},
            "low": {"label": low.get(dim, "N/A"), "value": low.get(meas, 0)},
            "measure_name": meas
        }

    if shape == 'COMPARISON':
        if len(rows) < 2: return {}
        a, b = rows[0], rows[1]
        
        a_val = a.get(meas, 0)
        b_val = b.get(meas, 0)
        
        a_val = a_val if isinstance(a_val, (int, float)) and not isinstance(a_val, bool) else 0
        b_val = b_val if isinstance(b_val, (int, float)) and not isinstance(b_val, bool) else 0
        
        pct_change = round(((b_val - a_val) / abs(a_val)) * 100, 1) if a_val else 0.0
        return {
            "a": {"label": a.get(dim, "N/A"), "value": a_val},
            "b": {"label": b.get(dim, "N/A"), "value": b_val},
            "pct_change": abs(pct_change),
            "direction": "up" if b_val >= a_val else "down",
            "measure_name": meas
        }
        
    if shape == 'TOP_N':
        valid_rows = [r for r in rows if isinstance(r.get(meas), (int, float)) and not isinstance(r.get(meas), bool)]
        valid_rows = sorted(valid_rows, key=lambda x: x.get(meas, 0), reverse=True)
        total = sum(r.get(meas, 0) for r in valid_rows)
        
        def get_pct(val, t): return round((val / t) * 100, 1) if t else 0.0
        
        items = [{"label": r.get(dim, "N/A"), "value": r.get(meas, 0), "pct": get_pct(r.get(meas, 0), total)} for r in valid_rows]
        leader = items[0] if items else {"label": "N/A", "value": 0, "pct": 0.0}
        
        return {
            "n": len(items),
            "items": items,
            "leader": leader,
            "measure_name": meas
        }

    return {}