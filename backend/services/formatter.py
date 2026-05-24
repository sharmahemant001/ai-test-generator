from typing import List, Dict, Any

def format_response(summary: str, coverage: int, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    normalized = []

    for case in test_cases:
        normalized.append({
            'id': case.get('id', ''),
            'type': case.get('type', 'functional'),
            'category': case.get('category', case.get('type', 'functional')).upper(),
            'title': case.get('title', ''),
            'description': case.get('description', ''),
            'input': case.get('input', ''),
            'expectedResult': case.get('expectedResult', ''),
            'expected': case.get('expectedResult', ''),
            'automationTemplate': case.get('automationTemplate'),
        })

    return {
        'summary': summary,
        'coverage': coverage,
        'testCases': normalized,
    }
