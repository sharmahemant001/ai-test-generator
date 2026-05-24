import unittest

from backend.services.parser import parse_requirements
from backend.services.rule_engine import build_test_cases
from backend.utils.coverage import estimate_coverage


PROFILE_REQUIREMENTS = """Profile API

Fields:

userEmail
homeAddress

Rules:

Email valid

Address required

Profile updates only when validations pass"""


PHONE_ALIAS_REQUIREMENTS = """Contact API

Fields:

mobileNumber
contactNumber

Rules:

Phone exactly 10

Contact succeeds only when validations pass"""


class ProfileSemanticConstraintTests(unittest.TestCase):
    def test_profile_semantic_rules_are_mapped_to_alias_fields(self):
        constraints = parse_requirements(PROFILE_REQUIREMENTS)

        self.assertEqual(constraints['fields']['userEmail'], {'type': 'email', 'required': True})
        self.assertEqual(constraints['fields']['homeAddress'], {'required': True, 'type': 'address'})
        self.assertEqual(constraints['success_condition'], 'business_flow')

    def test_profile_semantic_cases_are_generated(self):
        constraints = parse_requirements(PROFILE_REQUIREMENTS)
        test_cases = build_test_cases(PROFILE_REQUIREMENTS, constraints)
        generated = {(case['title'], case['input'], case['expectedResult']) for case in test_cases}

        self.assertIn(
            (
                'userEmail valid email',
                '{"userEmail":"user@gmail.com"}',
                'Validation succeeds for a valid userEmail email address.',
            ),
            generated,
        )
        self.assertIn(
            (
                'userEmail missing @ symbol',
                '{"userEmail":"usergmail.com"}',
                'Validation fails because userEmail has an email format error.',
            ),
            generated,
        )
        self.assertTrue(any(case['title'] == 'userEmail missing while required' for case in test_cases))
        self.assertIn(
            (
                'homeAddress valid address',
                '{"homeAddress":"221B Baker Street"}',
                'Validation succeeds for a valid homeAddress.',
            ),
            generated,
        )
        self.assertTrue(any(case['title'] == 'homeAddress missing while required' for case in test_cases))
        self.assertTrue(any(case['expectedResult'] == 'Profile updates success' for case in test_cases))

        coverage = estimate_coverage(test_cases, constraints['fields'], constraints['success_condition'])
        self.assertGreater(coverage['coverage_score'], 57)

    def test_phone_rules_map_to_phone_aliases(self):
        constraints = parse_requirements(PHONE_ALIAS_REQUIREMENTS)

        self.assertEqual(constraints['fields']['mobileNumber']['exact_length'], 10)
        self.assertEqual(constraints['fields']['contactNumber']['exact_length'], 10)

        test_cases = build_test_cases(PHONE_ALIAS_REQUIREMENTS, constraints)
        generated_titles = {case['title'] for case in test_cases}

        self.assertIn('mobileNumber meets required length', generated_titles)
        self.assertIn('contactNumber meets required length', generated_titles)


if __name__ == '__main__':
    unittest.main()
