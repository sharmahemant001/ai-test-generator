import unittest

from backend.services.parser import parse_requirements
from backend.services.rule_engine import build_test_cases


class GenericExactLengthTests(unittest.TestCase):
    def test_zipcode_exact_length_generates_boundaries(self):
        requirements = 'Zipcode exactly 6'
        constraints = parse_requirements(requirements)
        test_cases = build_test_cases(requirements, constraints)
        generated = {(case['title'], case['input'], case['expectedResult']) for case in test_cases}
        categories = {case['title']: case['category'] for case in test_cases}

        self.assertEqual(constraints['fields']['zipcode']['exact_length'], 6)
        self.assertIn(
            (
                'zipcode below required length',
                '{"zipcode":"12345"}',
                'Validation fails because zipcode is too short.',
            ),
            generated,
        )
        self.assertIn(
            (
                'zipcode exact length',
                '{"zipcode":"123456"}',
                'Validation succeeds for zipcode with the exact length.',
            ),
            generated,
        )
        self.assertIn(
            (
                'zipcode above required length',
                '{"zipcode":"1234567"}',
                'Validation fails because zipcode is too long.',
            ),
            generated,
        )

    def test_custom_exact_length_field_generates_boundaries(self):
        requirements = """Account API

Fields:

accountNumber

Rules:

AccountNumber exact 12

Account succeeds only when validations pass"""
        constraints = parse_requirements(requirements)
        test_cases = build_test_cases(requirements, constraints)
        generated = {(case['title'], case['input'], case['expectedResult']) for case in test_cases}
        categories = {case['title']: case['category'] for case in test_cases}

        self.assertEqual(constraints['fields']['accountNumber']['exact_length'], 12)
        self.assertIn(
            (
                'accountNumber below required length',
                '{"accountNumber":"12345678901"}',
                'Validation fails because accountNumber is too short.',
            ),
            generated,
        )
        self.assertIn(
            (
                'accountNumber exact length',
                '{"accountNumber":"123456789012"}',
                'Validation succeeds for accountNumber with the exact length.',
            ),
            generated,
        )
        self.assertIn(
            (
                'accountNumber above required length',
                '{"accountNumber":"1234567890123"}',
                'Validation fails because accountNumber is too long.',
            ),
            generated,
        )
        self.assertEqual(categories['accountNumber below required length'], 'BOUNDARY')
        self.assertEqual(categories['accountNumber exact length'], 'BOUNDARY')
        self.assertEqual(categories['accountNumber above required length'], 'BOUNDARY')
        self.assertIn(
            (
                'Business flow succeeds with all valid fields',
                '{"accountNumber":"123456789012"}',
                'Validation succeeds when all fields are valid.',
            ),
            generated,
        )


if __name__ == '__main__':
    unittest.main()
