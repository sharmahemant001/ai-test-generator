import re
from typing import List, Dict, Any


def estimate_coverage(test_cases: List[Dict[str, Any]], fields: Dict[str, Any], success_condition: str = '') -> Dict[str, Any]:
    field_coverage = {field: False for field in fields}
    category_coverage = {
        'functional': False,
        'boundary': False,
        'negative': False,
        'edge': False,
        'business_flow': False,
    }

    for case in test_cases:
        case_type = case.get('type', 'functional')
        if case_type in category_coverage:
            category_coverage[case_type] = True

        if case_type == 'functional' and 'flow' in case.get('title', '').lower():
            category_coverage['business_flow'] = True

        input_payload = case.get('input', '')
        for field in fields:
            if re.search(rf'"{field}"\s*:', input_payload):
                field_coverage[field] = True

    business_flow_coverage = category_coverage['business_flow']

    expected_fields = len(fields)
    expected_categories = len(category_coverage)
    expected_items = expected_fields + expected_categories

    covered_items = sum(field_coverage.values()) + sum(category_coverage.values())
    coverage_score = int((covered_items / expected_items) * 100) if expected_items else 100

    return {
        'coverage_score': coverage_score,
        'field_coverage': field_coverage,
        'category_coverage': category_coverage,
        'business_flow_coverage': business_flow_coverage,
    }
