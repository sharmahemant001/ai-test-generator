import unittest

from backend.services.parser import parse_requirements
from backend.services.rule_engine import build_test_cases
from backend.utils.coverage import estimate_coverage


CHECKOUT_REQUIREMENTS = """Checkout API

Fields:

customerEmail
deliveryAddress
contactNumber

Rules:

Email valid

Address required

Phone exactly 10

Checkout succeeds only when validations pass"""


class CheckoutAliasResolutionTests(unittest.TestCase):
    def test_semantic_aliases_attach_to_explicit_fields_without_duplicates(self):
        constraints = parse_requirements(CHECKOUT_REQUIREMENTS)

        self.assertEqual(set(constraints['fields']), {'customerEmail', 'deliveryAddress', 'contactNumber'})
        self.assertEqual(constraints['fields']['customerEmail'], {'type': 'email', 'required': True})
        self.assertEqual(constraints['fields']['deliveryAddress'], {'required': True, 'type': 'address'})
        self.assertEqual(constraints['fields']['contactNumber'], {'exact_length': 10, 'required': True})

    def test_generated_cases_use_explicit_fields_only(self):
        constraints = parse_requirements(CHECKOUT_REQUIREMENTS)
        test_cases = build_test_cases(CHECKOUT_REQUIREMENTS, constraints)
        generated = {(case['title'], case['input'], case['expectedResult']) for case in test_cases}

        self.assertIn(
            (
                'customerEmail missing @ symbol',
                '{"customerEmail":"usergmail.com"}',
                'Validation fails because customerEmail has an email format error.',
            ),
            generated,
        )
        self.assertIn(
            (
                'deliveryAddress empty address',
                '{"deliveryAddress":""}',
                'Validation fails because deliveryAddress is required.',
            ),
            generated,
        )
        self.assertIn(
            (
                'contactNumber meets required length',
                '{"contactNumber":"9999999999"}',
                'Validation succeeds for contactNumber with the required length.',
            ),
            generated,
        )
        self.assertFalse(any('"email":' in case['input'] for case in test_cases))
        self.assertFalse(any('"phone":' in case['input'] for case in test_cases))
        self.assertFalse(any('"Address":' in case['input'] for case in test_cases))
        self.assertIn(
            (
                'Business flow succeeds with all valid fields',
                '{"customerEmail":"user@gmail.com","contactNumber":"9876543210","deliveryAddress":"221B Baker Street"}',
                'Validation succeeds when all fields are valid.',
            ),
            generated,
        )

        coverage = estimate_coverage(test_cases, constraints['fields'], constraints['success_condition'])
        self.assertEqual(coverage['coverage_score'], 100)


if __name__ == '__main__':
    unittest.main()
