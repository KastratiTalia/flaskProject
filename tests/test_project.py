# The HTTP status code
# The response payload
# The response headers
# The API performance/response time


import unittest
from app import app
from app import db, UserInfo, UserSpending, get_age_group
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

    def test_get_all_users(self):
        """Test the get_all_users endpoint"""

        expected_user_count = 3000

        response = self.app.get(f'{self.URL}/users')

        # Check status code
        self.assertEqual(response.status_code, 200)

        # Check response data
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(response_data, list)

        self.assertEqual(len(response_data), expected_user_count)

        # Check that each user in the response has the expected keys
        expected_user_keys = ['user_id', 'name', 'email', 'age']
        for user in response_data:
            self.assertIsInstance(user, dict)
            for key in expected_user_keys:
                self.assertIn(key, user)

        print("Test get_all_users completed")

    def test_2_get_user_by_id(self):
        """ Test_2: get user by id """
        resp = self.app.get(f"{self.URL}/users/{self.user_id}")
        response_json = resp.get_json()

        self.assertEqual(resp.status_code, 200)

        self.assertIsNotNone(response_json, "Response JSON is None")
        self.assertDictEqual(response_json, self.expected_result_dict)

        print("Test 2 completed")

    def test_user_not_found(self):
        """Test for user not found scenario"""
        user_id = 4000

        response = self.app.get(f"{self.URL}/users/{user_id}")
        response_json = response.get_json()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_json['error'], "User not found")

        print("User not found test completed")

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

    def test_average_spending_user_not_found(self):
        """Test when user is not found"""
        user_id = 4000

        response = self.app.get(f'{self.URL + '/average_spending_by_age'}/{user_id}')

        self.assertEqual(response.status_code, 404)

        self.assertEqual(response.data.decode('utf-8'), 'User not found')

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

    def test_write_to_mongodb_successful(self):
        """Test successful data insertion"""

        data = {"user_id": 222, "total_spending": 2500}
        headers = {"Content-Type": "application/json"}

        response = self.app.post(self.URL + '/write_to_mongodb', data=json.dumps(data), headers=headers)
        response_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response_data['success'], 'Data was successfully inserted')

    def test_write_to_mongodb_existing_user(self):
        """Test when user already exists"""
        data = {"user_id": 123, "total_spending": 2500}
        headers = {"Content-Type": "application/json"}

        # Inserting the same user data before the test
        self.app.post(self.URL + '/write_to_mongodb', data=json.dumps(data), headers=headers)

        response = self.app.post(self.URL + '/write_to_mongodb', data=json.dumps(data), headers=headers)
        response_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['error'], f'User with user_id {data["user_id"]} already exists!')

    def test_write_to_mongodb_missing_parameters(self):
        """Test when user_id or total_spending parameter is missing"""
        data = {"total_spending": 2500}
        headers = {"Content-Type": "application/json"}

        response = self.app.post(self.URL + '/write_to_mongodb', data=json.dumps(data), headers=headers)
        response_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['error'], 'Missing user_id or total_spending parameter')

    def test_write_to_mongodb_invalid_total_spending(self):
        """Test when total_spending is less than 2000"""
        data = {"user_id": 333, "total_spending": 1500}
        headers = {"Content-Type": "application/json"}

        response = self.app.post(self.URL + '/write_to_mongodb', data=json.dumps(data), headers=headers)
        response_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['error'], 'Total spending must be greater than 2000!')


if __name__ == '__main__':
    unittest.main()
