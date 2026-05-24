import unittest

from backend.services.parser import parse_requirements
from backend.services.rule_engine import build_test_cases


REGISTRATION_REQUIREMENTS = """Registration API

Rules:

Email valid

Password minimum 8

Phone exactly 10

Registration succeeds only when validations pass"""


class RegistrationNormalizationTests(unittest.TestCase):
    def test_known_fields_are_normalized_and_deduplicated(self):
        constraints = parse_requirements(REGISTRATION_REQUIREMENTS)

        self.assertEqual(set(constraints['fields']), {'email', 'password', 'phone'})
        self.assertEqual(constraints['fields']['email'], {'type': 'email', 'required': True})
        self.assertEqual(constraints['fields']['password'], {'min_length': 8, 'required': True})
        self.assertEqual(constraints['fields']['phone'], {'exact_length': 10, 'required': True})

    def test_password_minimum_generates_string_length_cases_only(self):
        constraints = parse_requirements(REGISTRATION_REQUIREMENTS)
        test_cases = build_test_cases(REGISTRATION_REQUIREMENTS, constraints)
        generated = {(case['title'], case['input'], case['expectedResult']) for case in test_cases}
        password_cases = [case for case in test_cases if 'password' in case['input']]

        self.assertIn(
            (
                'Password shorter than minimum length',
                '{"password":"xxxxxxx"}',
                'Validation fails because password is too short.',
            ),
            generated,
        )
        self.assertIn(
            (
                'Password at minimum length',
                '{"password":"xxxxxxxx"}',
                'Validation succeeds for password at minimum length.',
            ),
            generated,
        )
        self.assertIn(
            (
                'Password longer than minimum length',
                '{"password":"xxxxxxxxx"}',
                'Validation succeeds for a password longer than the minimum length.',
            ),
            generated,
        )
        self.assertFalse(any('"Password":8' in case['input'] for case in test_cases))
        self.assertFalse(any('"password":8' in case['input'] for case in password_cases))


if __name__ == '__main__':
    unittest.main()
