STANDARD_FIXTURES = {
    "count": {
        "rows": [{"count": 759}],
        "hints": {"intent": "count", "entity": "orders"}
    },
    "grouped": {
        "rows": [{"status": "Approved", "count": 759}, {"status": "Rejected", "count": 209}],
        "hints": {"intent": "grouped", "dimension": "status", "measure": "count"}
    },
    "trend": {
        "rows": [
            {"month": "Jan", "sales": 100}, 
            {"month": "Feb", "sales": 120}, 
            {"month": "Mar", "sales": 180}
        ],
        "hints": {"intent": "trend", "dimension": "month", "measure": "sales"}
    },
    "comparison": {
        "rows": [{"period": "last", "sales": 100}, {"period": "this", "sales": 112}],
        "hints": {"intent": "comparison", "dimension": "period", "measure": "sales"}
    },
    "top_n": {
        "rows": [
            {"name": "A", "total": 50}, 
            {"name": "B", "total": 30}, 
            {"name": "C", "total": 20}
        ],
        "hints": {"intent": "top_n", "dimension": "name", "measure": "total"}
    },
    "single": {
        "rows": [{"id": 7, "status": "Open", "owner": "Sam"}],
        "hints": {"intent": "single"}
    },
    "empty": {
        "rows": [], 
        "hints": {}
    },
    "unknown": {
        "rows": [{"id": 1, "name": "foo", "val": 99}], 
        "hints": {}
    }
}

EDGE_FIXTURES = {
    "empty_with_hint": {"rows": [], "hints": {"intent": "trend"}},
    "single_group_grouped": {"rows": [{"status": "Approved", "count": 100}], "hints": {"intent": "grouped"}},
    "tie_top_bottom": {"rows": [{"name": "A", "val": 50}, {"name": "B", "val": 50}], "hints": {"intent": "top_n"}},
    "total_zero": {"rows": [{"status": "A", "count": 0}, {"status": "B", "count": 0}], "hints": {"intent": "grouped"}},
    "negative_values": {"rows": [{"month": "Jan", "profit": -50}, {"month": "Feb", "profit": 10}], "hints": {"intent": "trend"}},
    "none_null_cells": {"rows": [{"name": "A", "val": None}, {"name": "B", "val": 20}], "hints": {"intent": "top_n"}},
    "mixed_types": {"rows": [{"col": "text", "val": 10}, {"col": 5, "val": "20"}], "hints": {}},
    "unicode_names": {"rows": [{"més": "Enero", "ventas": 100}], "hints": {"intent": "trend"}},
    "10k_rows": {"rows": [{"id": i, "val": i*2} for i in range(10000)], "hints": {"intent": "grouped"}}
}