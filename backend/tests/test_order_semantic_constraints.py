import unittest
from datetime import date, timedelta

from backend.services.parser import parse_requirements
from backend.services.rule_engine import build_test_cases
from backend.utils.coverage import estimate_coverage


ORDER_REQUIREMENTS = """Order API

Fields:

customerEmail
amount
coupon
shippingAddress
phone
deliveryDate

Rules:

Email valid

Amount >0

Maximum amount 100000

Coupon optional

Phone exactly 10

Delivery date future only

Address required

Order succeeds only when validations pass"""


class OrderSemanticConstraintTests(unittest.TestCase):
    def test_semantic_rules_are_mapped_to_related_fields(self):
        constraints = parse_requirements(ORDER_REQUIREMENTS)

        self.assertEqual(constraints['fields']['customerEmail']['type'], 'email')
        self.assertTrue(constraints['fields']['customerEmail']['required'])
        self.assertEqual(
            constraints['fields']['shippingAddress'],
            {'required': True, 'type': 'address'},
        )
        self.assertEqual(
            constraints['fields']['deliveryDate'],
            {'required': True, 'type': 'date', 'future_only': True},
        )
        self.assertEqual(constraints['fields']['phone']['exact_length'], 10)
        self.assertEqual(constraints['fields']['amount']['range'], {'min': 1, 'max': 100000})
        self.assertFalse(constraints['fields']['coupon']['required'])

    def test_semantic_rule_cases_are_generated(self):
        constraints = parse_requirements(ORDER_REQUIREMENTS)
        test_cases = build_test_cases(ORDER_REQUIREMENTS, constraints)
        generated = {(case['title'], case['input'], case['expectedResult']) for case in test_cases}

        yesterday = (date.today() - timedelta(days=1)).isoformat()
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()

        self.assertIn(
            (
                'customerEmail missing @ symbol',
                '{"customerEmail":"usergmail.com"}',
                'Validation fails because customerEmail has an email format error.',
            ),
            generated,
        )
        self.assertTrue(any(case['title'] == 'customerEmail missing while required' for case in test_cases))
        self.assertIn(
            (
                'shippingAddress empty address',
                '{"shippingAddress":""}',
                'Validation fails because shippingAddress is required.',
            ),
            generated,
        )
        self.assertIn(
            (
                'deliveryDate past date',
                f'{{"deliveryDate":"{yesterday}"}}',
                'Validation fails because deliveryDate must be a future date.',
            ),
            generated,
        )
        self.assertIn(
            (
                'deliveryDate today',
                f'{{"deliveryDate":"{today}"}}',
                'Validation fails because deliveryDate must be after today.',
            ),
            generated,
        )
        self.assertIn(
            (
                'deliveryDate tomorrow',
                f'{{"deliveryDate":"{tomorrow}"}}',
                'Validation succeeds because deliveryDate is in the future.',
            ),
            generated,
        )

        coverage = estimate_coverage(test_cases, constraints['fields'], constraints['success_condition'])
        self.assertEqual(coverage['coverage_score'], 100)


if __name__ == '__main__':
    unittest.main()
