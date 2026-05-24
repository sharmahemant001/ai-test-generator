import unittest

from backend.services.parser import parse_requirements
from backend.services.rule_engine import build_test_cases
from backend.utils.coverage import estimate_coverage


LOAN_REQUIREMENTS = """Loan API

Rules:

loanAmount >= 5000

loanAmount <= 500000

PAN required

employmentType optional

Loan approved only when validations pass"""


class LoanInferredConstraintTests(unittest.TestCase):
    def test_fields_are_inferred_from_rule_lines_without_fields_section(self):
        constraints = parse_requirements(LOAN_REQUIREMENTS)

        self.assertEqual(
            constraints['fields']['loanAmount'],
            {'range': {'min': 5000, 'max': 500000}, 'type': 'numeric', 'required': True},
        )
        self.assertEqual(constraints['fields']['PAN'], {'required': True})
        self.assertEqual(constraints['fields']['employmentType'], {'required': False})
        self.assertEqual(constraints['success_condition'], 'loan approved')

    def test_inferred_loan_rules_generate_boundaries_and_business_flow(self):
        constraints = parse_requirements(LOAN_REQUIREMENTS)
        test_cases = build_test_cases(LOAN_REQUIREMENTS, constraints)
        generated = {(case['title'], case['input'], case['expectedResult']) for case in test_cases}

        self.assertIn(
            (
                'Loanamount below minimum',
                '{"loanAmount":4999}',
                'Validation fails because loanAmount is below the allowed minimum.',
            ),
            generated,
        )
        self.assertIn(
            (
                'Loanamount at minimum boundary',
                '{"loanAmount":5000}',
                'Validation succeeds for the minimum allowed loanAmount.',
            ),
            generated,
        )
        self.assertIn(
            (
                'Loanamount at maximum boundary',
                '{"loanAmount":500000}',
                'Validation succeeds for the maximum allowed loanAmount.',
            ),
            generated,
        )
        self.assertIn(
            (
                'Loanamount above maximum',
                '{"loanAmount":500001}',
                'Validation fails because loanAmount is above the allowed maximum.',
            ),
            generated,
        )
        self.assertIn(
            (
                'PAN missing while required',
                '{"loanAmount":5000,"employmentType":"valid"}',
                'Validation fails because PAN is required.',
            ),
            generated,
        )
        self.assertIn(
            (
                'Employmenttype omitted while optional',
                '{"loanAmount":5000,"PAN":"valid"}',
                'Validation succeeds when all fields are valid.',
            ),
            generated,
        )
        self.assertIn(
            (
                'Business flow succeeds with all valid fields',
                '{"loanAmount":5000,"PAN":"valid","employmentType":"valid"}',
                'Validation succeeds when all fields are valid.',
            ),
            generated,
        )

        coverage = estimate_coverage(test_cases, constraints['fields'], constraints['success_condition'])
        self.assertGreater(coverage['coverage_score'], 70)


if __name__ == '__main__':
    unittest.main()
