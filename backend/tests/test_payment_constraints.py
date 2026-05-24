import unittest

from backend.services.parser import parse_requirements
from backend.services.rule_engine import build_test_cases
from backend.utils.coverage import estimate_coverage


PAYMENT_REQUIREMENTS = """Payment API

Amount > 0

Currency required

Coupon optional

Maximum amount 50000

Payment succeeds only when validations pass"""


class PaymentConstraintTests(unittest.TestCase):
    def test_payment_constraints_are_extracted(self):
        constraints = parse_requirements(PAYMENT_REQUIREMENTS)

        self.assertEqual(
            constraints['fields']['amount'],
            {'range': {'min': 1, 'max': 50000}, 'type': 'numeric', 'required': True},
        )
        self.assertEqual(constraints['fields']['currency'], {'required': True})
        self.assertEqual(constraints['fields']['coupon'], {'required': False})

    def test_payment_boundaries_and_optional_omission_are_generated(self):
        constraints = parse_requirements(PAYMENT_REQUIREMENTS)
        test_cases = build_test_cases(PAYMENT_REQUIREMENTS, constraints)
        generated = {(case['title'], case['input'], case['expectedResult']) for case in test_cases}

        self.assertIn(
            ('Amount below minimum', '{"amount":0}', 'Validation fails because amount is below the allowed minimum.'),
            generated,
        )
        self.assertIn(
            ('Amount at minimum boundary', '{"amount":1}', 'Validation succeeds for the minimum allowed amount.'),
            generated,
        )
        self.assertIn(
            ('Amount at maximum boundary', '{"amount":50000}', 'Validation succeeds for the maximum allowed amount.'),
            generated,
        )
        self.assertIn(
            ('Amount above maximum', '{"amount":50001}', 'Validation fails because amount is above the allowed maximum.'),
            generated,
        )
        self.assertIn(
            ('Coupon omitted while optional', '{"amount":1000,"currency":"USD"}', 'Payment Success'),
            generated,
        )

        coverage = estimate_coverage(test_cases, constraints['fields'], constraints['success_condition'])
        self.assertGreater(coverage['coverage_score'], 40)


if __name__ == '__main__':
    unittest.main()
