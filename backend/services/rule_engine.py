from typing import Dict, Any, List
from datetime import date, timedelta
import json
import uuid

ConstraintSet = Dict[str, Any]


def _make_id(prefix: str) -> str:
    return f'{prefix}-{uuid.uuid4().hex[:8]}'


def _render_input(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, separators=(',', ':'))


def _add_case(results: List[Dict[str, Any]], category: str, title: str, description: str, payload: Dict[str, Any], expected: str) -> None:
    results.append({
        'id': _make_id(category.lower()),
        'type': category.lower(),
        'category': category.upper(),
        'title': title,
        'description': description,
        'input': _render_input(payload),
        'expectedResult': expected,
        'expected': expected,
    })


def _success_expected(requirements: str) -> str:
    if 'payment' in requirements.lower():
        return 'Payment Success'
    if 'order' in requirements.lower():
        return 'Order Success'
    if 'profile' in requirements.lower():
        return 'Profile updates success'
    if 'signup' in requirements.lower():
        return 'Signup succeeds when all fields are valid.'
    return 'Validation succeeds when all fields are valid.'


def _numeric_valid_value(field: str, field_range: Dict[str, Any]) -> Any:
    minimum = field_range.get('min')
    maximum = field_range.get('max')

    if field == 'amount':
        candidate = 1000
        if minimum is not None and candidate < minimum:
            candidate = minimum
        if maximum is not None and candidate > maximum:
            candidate = maximum
        return candidate

    if minimum is not None:
        return minimum
    if maximum is not None:
        return maximum
    return 1


def _default_valid_value(field: str, config: Dict[str, Any]) -> Any:
    if 'exact_length' in config:
        return _exact_length_value(field, config['exact_length'])
    if config.get('type') == 'numeric' or 'range' in config:
        return _numeric_valid_value(field, config.get('range', {}))
    if config.get('type') == 'email' or 'email' in field.lower():
        return 'user@gmail.com'
    if config.get('type') == 'address' or 'address' in field.lower():
        return '221B Baker Street'
    if config.get('type') == 'date':
        return (date.today() + timedelta(days=1)).isoformat()
    if field == 'currency':
        return 'USD'
    if field == 'coupon':
        return 'SAVE10'
    if field == 'card':
        return '4111111111111111'
    if field == 'zipcode':
        return '12345'
    return 'valid'


def _is_phone_field(field: str) -> bool:
    field_key = field.lower()
    return any(alias in field_key for alias in ['phone', 'mobile', 'contactnumber', 'mobilenumber'])


def _exact_length_value(field: str, length: int) -> str:
    field_key = field.lower()
    if any(token in field_key for token in ['zip', 'phone', 'contactnumber', 'mobile', 'account', 'id']):
        digits = '1234567890'
        return (digits * ((max(length, 0) // len(digits)) + 1))[:max(length, 0)]
    return 'x' * max(length, 0)


def build_test_cases(requirements: str, constraints: ConstraintSet) -> List[Dict[str, Any]]:
    fields = constraints.get('fields', {})
    success_condition = constraints.get('success_condition', '')
    results: List[Dict[str, Any]] = []
    valid_payload: Dict[str, Any] = {}

    email_fields = [
        field for field, config in fields.items()
        if config.get('type') == 'email' or 'email' in field.lower()
    ]
    for field in email_fields:
        _add_case(
            results,
            'FUNCTIONAL',
            f'{field} valid email',
            f'{field} should pass when email format is valid.',
            {field: 'user@gmail.com'},
            f'Validation succeeds for a valid {field} email address.',
        )
        _add_case(
            results,
            'EDGE',
            f'{field} complex email',
            f'{field} should accept a plus alias and subdomain format.',
            {field: 'user+test@mail.example.com'},
            f'Validation succeeds for a complex valid {field} email address.',
        )
        _add_case(
            results,
            'NEGATIVE',
            f'{field} missing @ symbol',
            f'{field} without the @ symbol must fail validation.',
            {field: 'usergmail.com'},
            f'Validation fails because {field} has an email format error.',
        )
        _add_case(
            results,
            'NEGATIVE',
            f'{field} missing domain',
            f'{field} with only the local part should fail validation.',
            {field: 'user@'},
            f'Validation fails because {field} has an email format error.',
        )
        _add_case(
            results,
            'NEGATIVE',
            f'{field} missing local part',
            f'{field} without a local part should fail validation.',
            {field: '@gmail.com'},
            f'Validation fails because {field} has an email format error.',
        )
        valid_payload[field] = 'user@gmail.com'

    if 'password' in fields:
        password_field = fields['password']
        min_length = password_field.get('min_length', 8)
        _add_case(
            results,
            'NEGATIVE',
            f'Password shorter than minimum length',
            f'Password with {min_length - 1} characters should fail minimum-length validation.',
            {'password': 'x' * max(min_length - 1, 1)},
            'Validation fails because password is too short.',
        )
        _add_case(
            results,
            'BOUNDARY',
            'Password at minimum length',
            f'Password with exactly {min_length} characters should pass boundary validation.',
            {'password': 'x' * min_length},
            'Validation succeeds for password at minimum length.',
        )
        _add_case(
            results,
            'FUNCTIONAL',
            'Password longer than minimum length',
            f'Password with {min_length + 1} characters should pass.',
            {'password': 'x' * (min_length + 1)},
            'Validation succeeds for a password longer than the minimum length.',
        )
        _add_case(
            results,
            'NEGATIVE',
            'Password is empty',
            'Password field should not accept an empty value.',
            {'password': ''},
            'Validation fails because password is required and must meet minimum length.',
        )
        valid_payload['password'] = 'x' * max(min_length, 8)

    phone_fields = [field for field in fields if _is_phone_field(field)]
    for field in phone_fields:
        phone_field = fields[field]
        exact_length = phone_field.get('exact_length', 10)
        _add_case(
            results,
            'BOUNDARY',
            f'{field} below required length',
            f'{field} with {exact_length - 1} digits should fail exact-length validation.',
            {field: '9' * max(exact_length - 1, 1)},
            f'Validation fails because {field} is too short.',
        )
        _add_case(
            results,
            'FUNCTIONAL',
            f'{field} meets required length',
            f'{field} with exactly {exact_length} digits should pass.',
            {field: '9' * exact_length},
            f'Validation succeeds for {field} with the required length.',
        )
        _add_case(
            results,
            'BOUNDARY',
            f'{field} above required length',
            f'{field} with {exact_length + 1} digits should fail exact-length validation.',
            {field: '9' * (exact_length + 1)},
            f'Validation fails because {field} is too long.',
        )
        _add_case(
            results,
            'NEGATIVE',
            f'{field} contains letters',
            f'{field} containing letters should fail numeric validation.',
            {field: '12345abcde'},
            f'Validation fails because {field} must contain only digits.',
        )
        _add_case(
            results,
            'NEGATIVE',
            f'{field} contains special characters',
            f'{field} containing symbols should fail validation.',
            {field: '12345!@#$%'},
            f'Validation fails because {field} must contain only digits.',
        )
        _add_case(
            results,
            'NEGATIVE',
            f'{field} is empty',
            f'Empty {field} should fail required field validation.',
            {field: ''},
            f'Validation fails because {field} is required.',
        )
        valid_payload[field] = '9876543210'

    for field, config in fields.items():
        if field in phone_fields or 'exact_length' not in config:
            continue

        exact_length = config['exact_length']
        below_value = _exact_length_value(field, exact_length - 1)
        valid_value = _exact_length_value(field, exact_length)
        above_value = _exact_length_value(field, exact_length + 1)
        _add_case(
            results,
            'BOUNDARY',
            f'{field} below required length',
            f'{field} with {exact_length - 1} characters should fail exact-length validation.',
            {field: below_value},
            f'Validation fails because {field} is too short.',
        )
        _add_case(
            results,
            'BOUNDARY',
            f'{field} exact length',
            f'{field} with exactly {exact_length} characters should pass.',
            {field: valid_value},
            f'Validation succeeds for {field} with the exact length.',
        )
        _add_case(
            results,
            'BOUNDARY',
            f'{field} above required length',
            f'{field} with {exact_length + 1} characters should fail exact-length validation.',
            {field: above_value},
            f'Validation fails because {field} is too long.',
        )
        valid_payload[field] = valid_value

    if 'age' in fields and 'range' in fields['age']:
        age_range = fields['age']['range']
        min_age = age_range['min']
        max_age = age_range['max']
        _add_case(
            results,
            'BOUNDARY',
            'Age below minimum',
            f'Age of {min_age - 1} should fail the lower bound.',
            {'age': min_age - 1},
            'Validation fails because age is below the allowed minimum.',
        )
        _add_case(
            results,
            'BOUNDARY',
            'Age at minimum boundary',
            f'Age of {min_age} should pass the lower boundary.',
            {'age': min_age},
            'Validation succeeds for the minimum allowed age.',
        )
        _add_case(
            results,
            'FUNCTIONAL',
            'Age within valid range',
            f'Age of {min_age + 1} should pass validation.',
            {'age': min_age + 1},
            'Validation succeeds for an age inside the allowed range.',
        )
        _add_case(
            results,
            'BOUNDARY',
            'Age at maximum boundary',
            f'Age of {max_age} should pass the upper boundary.',
            {'age': max_age},
            'Validation succeeds for the maximum allowed age.',
        )
        _add_case(
            results,
            'BOUNDARY',
            'Age above maximum',
            f'Age of {max_age + 1} should fail the upper bound.',
            {'age': max_age + 1},
            'Validation fails because age is above the allowed maximum.',
        )
        valid_payload['age'] = min_age + 1

    for field, config in fields.items():
        if field == 'age' or 'range' not in config or config.get('type') != 'numeric':
            continue

        field_range = config['range']
        if 'min' in field_range:
            minimum = field_range['min']
            _add_case(
                results,
                'BOUNDARY',
                f'{field.capitalize()} below minimum',
                f'{field.capitalize()} of {minimum - 1} should fail the lower bound.',
                {field: minimum - 1},
                f'Validation fails because {field} is below the allowed minimum.',
            )
            _add_case(
                results,
                'BOUNDARY',
                f'{field.capitalize()} at minimum boundary',
                f'{field.capitalize()} of {minimum} should pass the lower boundary.',
                {field: minimum},
                f'Validation succeeds for the minimum allowed {field}.',
            )

        if 'max' in field_range:
            maximum = field_range['max']
            _add_case(
                results,
                'BOUNDARY',
                f'{field.capitalize()} at maximum boundary',
                f'{field.capitalize()} of {maximum} should pass the upper boundary.',
                {field: maximum},
                f'Validation succeeds for the maximum allowed {field}.',
            )
            _add_case(
                results,
                'BOUNDARY',
                f'{field.capitalize()} above maximum',
                f'{field.capitalize()} of {maximum + 1} should fail the upper bound.',
                {field: maximum + 1},
                f'Validation fails because {field} is above the allowed maximum.',
            )

        valid_payload[field] = _numeric_valid_value(field, field_range)

    for field, config in fields.items():
        if config.get('type') != 'address' and 'address' not in field.lower():
            continue

        _add_case(
            results,
            'FUNCTIONAL',
            f'{field} valid address',
            f'{field} should pass when a non-empty address is provided.',
            {field: '221B Baker Street'},
            f'Validation succeeds for a valid {field}.',
        )
        _add_case(
            results,
            'NEGATIVE',
            f'{field} empty address',
            f'{field} should fail when address is empty.',
            {field: ''},
            f'Validation fails because {field} is required.',
        )
        valid_payload[field] = '221B Baker Street'

    for field, config in fields.items():
        if config.get('type') != 'date' or not config.get('future_only'):
            continue

        yesterday = date.today() - timedelta(days=1)
        today = date.today()
        tomorrow = date.today() + timedelta(days=1)
        future_date = date.today() + timedelta(days=30)

        _add_case(
            results,
            'NEGATIVE',
            f'{field} past date',
            f'{field} should fail when the date is in the past.',
            {field: yesterday.isoformat()},
            f'Validation fails because {field} must be a future date.',
        )
        _add_case(
            results,
            'BOUNDARY',
            f'{field} today',
            f'{field} should fail when future-only validation receives today.',
            {field: today.isoformat()},
            f'Validation fails because {field} must be after today.',
        )
        _add_case(
            results,
            'BOUNDARY',
            f'{field} tomorrow',
            f'{field} should pass with tomorrow as the first valid future date.',
            {field: tomorrow.isoformat()},
            f'Validation succeeds because {field} is in the future.',
        )
        _add_case(
            results,
            'FUNCTIONAL',
            f'{field} future valid date',
            f'{field} should pass with a valid future date.',
            {field: future_date.isoformat()},
            f'Validation succeeds because {field} is a valid future date.',
        )
        _add_case(
            results,
            'NEGATIVE',
            f'{field} invalid date format',
            f'{field} should fail when the date format is invalid.',
            {field: '31-12-2026'},
            f'Validation fails because {field} must use a valid date format.',
        )
        valid_payload[field] = tomorrow.isoformat()

    for field, config in fields.items():
        if field not in valid_payload:
            valid_payload[field] = _default_valid_value(field, config)

    for field, config in fields.items():
        if config.get('required'):
            payload = dict(valid_payload)
            payload.pop(field, None)
            _add_case(
                results,
                'NEGATIVE',
                f'{field} missing while required',
                f'{field} is required and missing values should fail validation.',
                payload,
                f'Validation fails because {field} is required.',
            )
        elif config.get('required') is False:
            payload = dict(valid_payload)
            payload.pop(field, None)
            _add_case(
                results,
                'FUNCTIONAL',
                f'{field.capitalize()} omitted while optional',
                f'{field.capitalize()} is optional and can be omitted from a valid request.',
                payload,
                _success_expected(requirements),
            )

    if success_condition and len(valid_payload) == len(fields):
        _add_case(
            results,
            'BUSINESS_FLOW',
            'Business flow succeeds with all valid fields',
            'A success path when all fields are valid and meet constraints.',
            valid_payload,
            _success_expected(requirements),
        )

        invalid_multiple = {}
        for field in fields:
            field_key = field.lower()
            if 'email' in field_key:
                invalid_multiple[field] = 'usergmail.com'
            elif field == 'password':
                invalid_multiple[field] = 'short'
            elif any(alias in field_key for alias in ['phone', 'mobile', 'contactnumber', 'mobilenumber']):
                invalid_multiple[field] = '12345abcde'
            elif field == 'age':
                invalid_multiple[field] = fields['age']['range']['min'] - 1 if 'range' in fields['age'] else 0

        if invalid_multiple:
            _add_case(
                results,
                'NEGATIVE',
                'Multiple invalid fields',
                'A combined invalid input with more than one field failing validation.',
                invalid_multiple,
                'Validation fails because multiple fields contain invalid values.',
            )

    unique = []
    seen = set()
    for case in results:
        key = (case['title'].strip().lower(), case['input'])
        if key not in seen:
            seen.add(key)
            unique.append(case)

    return unique
