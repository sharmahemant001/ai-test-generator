import unittest

from backend.main import app
from backend.services.parser import parse_requirements


class InvalidRequirementTests(unittest.TestCase):
    def test_garbage_input_returns_parser_error(self):
        for requirements in [
            'asdf qwerty banana mango',
            'hello world',
            'test api random words',
            'asdf qwerty zxczxc random api banana mango',
        ]:
            with self.subTest(requirements=requirements):
                self.assertEqual(
                    parse_requirements(requirements),
                    {
                        'error': 'Unable to extract requirements',
                        'message': 'Provide API specs or feature requirements',
                    },
                )

    def test_minimal_valid_requirements_pass_confidence_threshold(self):
        for requirements in [
            'Email required',
            'Password min 8',
            'Phone exactly 10',
        ]:
            with self.subTest(requirements=requirements):
                self.assertNotIn('error', parse_requirements(requirements))

    def test_generate_returns_400_for_unextractable_requirements(self):
        client = app.test_client()
        response = client.post('/generate', json={'requirements': 'asdf qwerty banana mango'})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.get_json(),
            {
                'error': 'Unable to extract requirements',
                'message': 'Provide API specs or feature requirements',
                'generated_tests': [],
            },
        )


if __name__ == '__main__':
    unittest.main()
