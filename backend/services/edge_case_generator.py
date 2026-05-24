from typing import List, Dict, Any


def expand_edge_cases(constraints: Dict[str, Any], existing_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    unique = []
    seen = set()

    for case in existing_cases:
        title = case.get('title', '').strip().lower()
        payload = case.get('input', '').strip()
        key = (title, payload)
        if key not in seen:
            seen.add(key)
            unique.append(case)

    return unique
