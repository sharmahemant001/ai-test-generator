import re
from typing import Dict, Any, List

KNOWN_FIELDS = ['email', 'password', 'phone', 'address', 'age', 'amount', 'currency', 'coupon', 'card', 'zipcode']

SEMANTIC_ALIASES = {
    'email': ['email', 'useremail', 'customeremail', 'subscriberemail', 'contactemail'],
    'phone': ['phone', 'contactnumber', 'mobilenumber', 'mobile', 'contactphone'],
    'address': ['address', 'deliveryaddress', 'shippingaddress', 'billingaddress', 'homeaddress'],
}

FieldConstraints = Dict[str, Any]
PARSER_ERROR = {
    'error': 'Unable to extract requirements',
    'message': 'Provide API fields, rules, or feature requirements',
}


def normalize(name: str) -> str:
    return name.strip().lower()


def _normalize_text(text: str) -> str:
    return text.replace('\r', '\n').lower()


def _parser_confidence(text: str) -> int:
    normalized = _normalize_text(text)
    confidence = 0

    if re.search(r'fields\s*:', text, re.I):
        confidence += 2

    validation_patterns = [
        r'\brequired\b',
        r'\boptional\b',
        r'\bminimum\b|\bmin\b',
        r'\bmaximum\b|\bmax\b',
        r'\bfuture only\b',
        r'\bvalid email\b|\bemail\s+valid\b',
        r'\bexactly\b',
        r'>=',
        r'<=',
        r'\b[A-Za-z][A-Za-z0-9_]*\s*(?:>|<)\s*\d+(?:\.\d+)?\b',
        r'\bnumeric\b|\bnumber\b',
    ]
    confidence += sum(1 for pattern in validation_patterns if re.search(pattern, normalized))

    if re.search(r'\bsucceeds only when\b|\bvalidations pass\b|\bsuccess only when\b', normalized):
        confidence += 2

    known_field_patterns = [
        r'\bemail\b',
        r'\bphone\b|\bcontactnumber\b|\bmobilenumber\b|\bmobile\b|\bcontactphone\b',
        r'\bamount\b',
        r'\bpassword\b',
        r'\bdate\b',
        r'\baddress\b',
        r'\bzipcode\b|\bzip\s*code\b',
    ]
    confidence += sum(1 for pattern in known_field_patterns if re.search(pattern, normalized))

    return confidence


def _extract_field_list(text: str) -> List[str]:
    match = re.search(r'fields\s*:\s*(.*?)(?:\n\s*\w+\s*:|$)', text, re.S | re.I)
    if not match:
        return []

    section = match.group(1)
    fields = re.findall(r'\b[A-Za-z][A-Za-z0-9_]*\b', section)
    return list(dict.fromkeys(fields))


def _detect_all_fields(text: str) -> List[str]:
    patterns = [
        r'\b(email|password|phone|address|age|amount|currency|coupon|card|zipcode)\b',
    ]
    detected = []
    for pattern in patterns:
        detected.extend(re.findall(pattern, text))
    return list(dict.fromkeys(detected))


def _infer_fields_from_rules(text: str) -> List[str]:
    inferred: List[str] = []
    patterns = [
        r'^\s*([A-Za-z][A-Za-z0-9_]*)\s*(?:>=|<=|>|<)\s*\d+(?:\.\d+)?\s*$',
        r'^\s*([A-Za-z][A-Za-z0-9_]*)\s+(?:required|optional|valid)\s*$',
        r'^\s*([A-Za-z][A-Za-z0-9_]*)\s+(?:exactly|minimum|maximum|min|max)\s+\d+(?:\.\d+)?\s*$',
    ]

    for line in text.splitlines():
        for pattern in patterns:
            match = re.search(pattern, line, re.I)
            if match:
                inferred.append(match.group(1))
                break

    return list(dict.fromkeys(inferred))


def _canonical_field_name(field: str) -> str:
    normalized = normalize(field)
    if normalized in KNOWN_FIELDS:
        return normalized
    return field


def _explicit_field_lookup(listed_fields: List[str]) -> Dict[str, str]:
    return {normalize(field): field for field in listed_fields}


def _merge_field_candidates(*candidate_groups: List[str]) -> List[str]:
    merged: Dict[str, str] = {}

    for group in candidate_groups:
        for field in group:
            canonical = _canonical_field_name(field)
            key = canonical.lower()
            if key not in merged:
                merged[key] = canonical

    return list(merged.values())


def _resolve_semantic_field_aliases(listed_fields: List[str], candidate_fields: List[str]) -> List[str]:
    if not listed_fields:
        return candidate_fields

    explicit_fields = _explicit_field_lookup(listed_fields)
    resolved = []
    for field in candidate_fields:
        field_key = normalize(_canonical_field_name(field))
        if any(
            field_key in aliases and any(_field_matches(explicit, concept) for explicit in explicit_fields.values())
            for concept, aliases in SEMANTIC_ALIASES.items()
        ):
            continue
        resolved.append(field)

    return resolved


def _dedupe_shadowed_semantic_aliases(fields: Dict[str, FieldConstraints], listed_fields: List[str]) -> None:
    if not listed_fields:
        return

    explicit_fields = _explicit_field_lookup(listed_fields)
    explicit_names = set(explicit_fields.values())

    for concept, aliases in SEMANTIC_ALIASES.items():
        has_explicit_semantic_field = any(
            _field_matches(explicit, concept) for explicit in explicit_fields.values()
        )
        if not has_explicit_semantic_field:
            continue

        for field_name in list(fields):
            if field_name in explicit_names:
                continue
            if normalize(_canonical_field_name(field_name)) in aliases:
                del fields[field_name]


def _field_key(field: str) -> str:
    return normalize(field)


def _field_words(field: str) -> List[str]:
    spaced = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', field)
    return re.findall(r'[a-z0-9]+', spaced.lower())


def _field_matches(field: str, concept: str) -> bool:
    key = _field_key(field)
    words = _field_words(field)
    concept = concept.lower()
    aliases = SEMANTIC_ALIASES.get(concept, [])

    if key in aliases or concept in key or concept in words:
        return True
    if concept == 'address':
        return 'address' in key
    if concept == 'date':
        return 'date' in key
    return False


def _field_required(field: str, text: str) -> bool:
    field_key = re.escape(_field_key(field))
    field_patterns = [
        rf'{field_key}\s+(?:is\s+)?required',
        rf'{field_key}\s+must be\s+(?:provided|supplied)',
        rf'required.*{field_key}',
    ]

    if _field_matches(field, 'address'):
        field_patterns.extend([
            r'address\s+(?:is\s+)?required',
            r'address\s+must be\s+(?:provided|supplied)',
            r'required.*address',
        ])
    
    if _field_optional(field, text):
        return False
    
    is_required = any(re.search(pattern, text) for pattern in field_patterns)
    return is_required


def _field_optional(field: str, text: str) -> bool:
    field_key = re.escape(_field_key(field))
    optional_patterns = [
        rf'{field_key}\s+(?:is\s+)?optional',
        rf'optional.*{field_key}',
    ]
    return any(re.search(pattern, text) for pattern in optional_patterns)


def _extract_numeric_constraints(field: str, text: str) -> Dict[str, Any]:
    constraints = {}
    field_key = re.escape(_field_key(field))

    patterns = [
        (r'>=\s*(\d+(?:\.\d+)?)', 'min'),
        (r'>\s*(\d+(?:\.\d+)?)', 'min_exclusive'),
        (r'<=\s*(\d+(?:\.\d+)?)', 'max'),
        (r'<\s*(\d+(?:\.\d+)?)', 'max_exclusive'),
        (rf'(?:minimum|min)\s+{field_key}\s+(\d+(?:\.\d+)?)', 'min'),
        (rf'{field_key}\s+(?:minimum|min)\s+(\d+(?:\.\d+)?)', 'min'),
        (rf'(?:maximum|max)\s+{field_key}\s+(\d+(?:\.\d+)?)', 'max'),
        (rf'{field_key}\s+(?:maximum|max)\s+(\d+(?:\.\d+)?)', 'max'),
        (r'(?:minimum|min|at least)\s*(\d+(?:\.\d+)?)', 'min'),
        (r'(?:maximum|max)\s*(\d+(?:\.\d+)?)', 'max'),
    ]

    for pattern, constraint_type in patterns:
        if field_key in pattern:
            field_pattern = pattern
        else:
            field_pattern = rf'{field_key}[^\n.]*?{pattern}'
        matches = re.finditer(field_pattern, text)
        for match in matches:
            value = float(match.group(1)) if '.' in match.group(1) else int(match.group(1))
            
            if constraint_type == 'min_exclusive':
                constraints['min'] = int(value) + 1
            elif constraint_type == 'max_exclusive':
                constraints['max'] = int(value) - 1
            elif constraint_type in constraints:
                continue
            else:
                constraints[constraint_type] = value
    
    return constraints


def _extract_enum_values(field: str, text: str) -> List[str]:
    """Extract allowed enum values from text."""
    field_key = re.escape(_field_key(field))
    normalized = text.replace('\n', ' ')

    patterns = [
        rf'{field_key}\s+(?:allowed\s+)?\b(?:values?|options?)\b\s*:?\s*([A-Za-z0-9_ ,]+)',
        rf'\b(?:allowed|valid)\b\s+{field_key}(?:\s+\bvalues?\b|\s+\boptions?\b)?\s*:?\s*([A-Za-z0-9_ ,]+)',
        rf'{field_key}\s+must\s+be\s+one\s+of\s+([A-Za-z0-9_ ,]+)',
        rf'{field_key}\s+may\s+be\s+one\s+of\s+([A-Za-z0-9_ ,]+)',
        rf'{field_key}\s*:\s*([A-Za-z0-9_ ,]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, normalized, re.I)
        if match:
            values_str = match.group(1)
            values = [v.strip() for v in re.split(r'[;,\s]+', values_str) if v.strip()]
            if len(values) > 1:
                return values

    return []


def _extract_password_rules(field: str, text: str) -> Dict[str, bool]:
    """Extract password complexity rules."""
    if field != 'password':
        return {}
    
    rules = {}
    normalized = text.lower()
    
    if re.search(r'password.*(?:must\s+)?contain.*uppercase|uppercase.*password', normalized):
        rules['require_uppercase'] = True
    if re.search(r'password.*(?:must\s+)?contain.*lowercase|lowercase.*password', normalized):
        rules['require_lowercase'] = True
    if re.search(r'password.*(?:must\s+)?contain.*(?:digit|number)|(?:digit|number).*password', normalized):
        rules['require_digit'] = True
    if re.search(r'password.*(?:must\s+)?contain.*(?:special|symbol|punctuation)|(?:special|symbol|punctuation).*password', normalized):
        rules['require_special'] = True
    
    return rules


def _extract_max_length(field: str, text: str) -> int:
    """Extract maximum length constraint."""
    field_key = re.escape(_field_key(field))
    
    patterns = [
        rf'{field_key}.*(?:maximum|max|up to)\s+(\d+)\s*(?:characters|chars?)',
        rf'(?:maximum|max|up to)\s+(\d+)\s*(?:characters|chars?)\s+.*{field_key}',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.I)
        if match:
            return int(match.group(1))
    
    return 0


def parse_requirements(text: str) -> Dict[str, Any]:
    if _parser_confidence(text) < 2:
        return dict(PARSER_ERROR)

    normalized = _normalize_text(text)
    fields: Dict[str, FieldConstraints] = {}

    listed_fields = _extract_field_list(text)
    inferred_fields = _infer_fields_from_rules(text)
    detected_fields = _detect_all_fields(normalized)
    inferred_fields = _resolve_semantic_field_aliases(listed_fields, inferred_fields)
    detected_fields = _resolve_semantic_field_aliases(listed_fields, detected_fields)
    active_fields = _merge_field_candidates(listed_fields, inferred_fields, detected_fields)

    for field_name in active_fields:
        fields[field_name] = {}

    for field_name in active_fields:
        if _field_matches(field_name, 'email'):
            if re.search(r'email.*(valid|format|must be valid|must match)', normalized):
                fields[field_name]['type'] = 'email'
            fields[field_name].setdefault('required', _field_required(field_name, normalized))

    if 'password' in fields:
        match = re.search(r'password.*(?:at least|minimum(?: of)?|>=?)\s*(\d+)(?:\s*(?:characters|chars?))?', normalized)
        if match:
            fields['password']['min_length'] = int(match.group(1))
        max_match = re.search(r'password.*(?:maximum|max(?:imum)?).*?(\d+)(?:\s*(?:characters|chars?))?', normalized)
        if max_match:
            fields['password']['max_length'] = int(max_match.group(1))
        # Extract password complexity rules
        password_rules = _extract_password_rules('password', normalized)
        fields['password'].update(password_rules)
        fields['password'].setdefault('required', _field_required('password', normalized))

    for field_name in active_fields:
        if _field_matches(field_name, 'phone'):
            match = re.search(r'phone.*exactly\s*(\d+)(?:\s*digits)?', normalized)
            if not match:
                match = re.search(r'(\d+)-digit phone', normalized)
            if match:
                fields[field_name]['exact_length'] = int(match.group(1))
            fields[field_name].setdefault('required', _field_required(field_name, normalized))

        if field_name not in ['email', 'password', 'phone', 'age']:
            enum_values = _extract_enum_values(field_name, normalized)
            if enum_values:
                fields[field_name]['enum'] = enum_values

            max_length = _extract_max_length(field_name, normalized)
            if max_length:
                fields[field_name]['max_length'] = max_length

    if 'age' in fields:
        match = re.search(r'age.*(?:between|from)\s*(\d+)\s*(?:and|-)\s*(\d+)', normalized)
        if match:
            fields['age']['range'] = {'min': int(match.group(1)), 'max': int(match.group(2))}
        fields['age'].setdefault('required', _field_required('age', normalized))

    for field_name in active_fields:
        if field_name not in ['email', 'password', 'phone', 'age']:
            exact_match = re.search(rf'{re.escape(_field_key(field_name))}\s+(?:exactly|exact)\s+(\d+)', normalized)
            if exact_match:
                fields[field_name]['exact_length'] = int(exact_match.group(1))

            numeric_constraints = _extract_numeric_constraints(field_name, normalized)
            if numeric_constraints:
                fields[field_name]['range'] = numeric_constraints
                fields[field_name]['type'] = 'numeric'
            
            fields[field_name].setdefault('required', _field_required(field_name, normalized))

        if _field_matches(field_name, 'address'):
            if re.search(r'address\s+(?:is\s+)?required|address\s+must be\s+(?:provided|supplied)|required.*address', normalized):
                fields[field_name]['type'] = 'address'
                fields[field_name]['required'] = True

        if _field_matches(field_name, 'date'):
            if re.search(r'(?:future only|future date|must be future|date\s+future only|delivery date\s+future only)', normalized):
                fields[field_name]['type'] = 'date'
                fields[field_name]['future_only'] = True

    success_condition = ''
    if re.search(r'loan approved', normalized):
        success_condition = 'loan approved'
    elif re.search(r'succeeds only when|updates only when|all fields valid|login success|payment succeeds|order succeeds|profile updates|success only when|payment success|login succeeds|validations pass', normalized):
        success_condition = 'business_flow'

    if success_condition:
        for field in fields:
            if not _field_optional(field, normalized):
                fields[field]['required'] = True

    _dedupe_shadowed_semantic_aliases(fields, listed_fields)

    if not fields and not success_condition:
        return dict(PARSER_ERROR)

    if not fields:
        return {
            'fields': {},
            'success_condition': success_condition,
        }

    return {
        'fields': fields,
        'success_condition': success_condition,
    }
