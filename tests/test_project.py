
# The HTTP status code
# The response payload
# The response headers
# The API performance/response time


import unittest
from app import app
import json


class TestProject(unittest.TestCase):

    URL = 'http://127.0.0.1:5000'

    user_id = 35

    expected_result_dict = {
        'user_id': user_id,
        'name': 'Tracy Orozco',
        'email': 'tracy_orozco@example.com',
        'age': 36
    }

    def setUp(self):
        self.app = app.test_client()

    def test_1_get_all_users(self):
        """ Test_1: get all users and user count """
        path = self.URL + '/users'
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 3000)

        print("Test 1 completed")

    def test_2_get_user_by_id(self):
        """ Test_2: get user by id """
        resp = self.app.get(self.URL + '/users/35')

        self.assertEqual(resp.status_code, 200)

        response_json = resp.get_json()

        self.assertIsNotNone(response_json, "Response JSON is None")
        self.assertDictEqual(response_json, self.expected_result_dict)

        print("Test 2 completed")

    def test_3_get_user_total_spending(self):
        """Test_3: Test for API 1"""
        response = self.app.get(f"{self.URL}/total_spent?user_id={self.user_id}")
        data = json.loads(response.data.decode('utf-8'))

        print(f"Response status code: {response.status_code}")
        print(f"Response JSON: {data}")

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data, "Response JSON is None")

        if 'error' in data:
            self.assertNotEqual(data['error'], 'User not found', "Unexpected 'User not found' error")
        else:
            expected_keys = ['user_id', 'name', 'age', 'total_spending']

            for key in expected_keys:
                self.assertIn(key, data, f"Key '{key}' not found in the response JSON")

            self.assertIsNotNone(data['user_id'], "User ID is None")
            self.assertIsNotNone(data['name'], "Name is None")
            self.assertIsNotNone(data['age'], "Age is None")
            self.assertIsNotNone(data['total_spending'], "Total spending is None")

        print(f"Test 3 completed for user_id {self.user_id}")

    def test_4_get_user_average_spending_by_age(self):
        """Test_4: Test for API 2 - average spending by age"""

        response = self.app.get(f"{self.URL}/average_spending_by_age/{self.user_id}")
        data = json.loads(response.data.decode('utf-8'))

        print(f"Response status code: {response.status_code}")
        print(f"Response JSON: {data}")

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(data, "Response JSON is None")

        if 'error' in data:
            self.assertNotEqual(data['error'], 'User not found', "Unexpected 'User not found' error")
        else:
            expected_keys = ['user_id', 'age', 'total_spending', 'age_group']

            for key in expected_keys:
                self.assertIn(key, data, f"Key '{key}' not found in the response JSON")

            self.assertIsNotNone(data['user_id'], "User ID is None")
            self.assertIsNotNone(data['age'], "Age is None")
            self.assertIsNotNone(data['total_spending'], "Total spending is None")
            self.assertIsNotNone(data['age_group'], "Age group is None")

        print(f"Test 4 completed for user_id {self.user_id}")






if __name__ == '__main__':
    unittest.main()
