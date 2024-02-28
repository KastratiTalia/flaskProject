import unittest
from pymongo import MongoClient
from app import app
import json


class TestProject(unittest.TestCase):
    """
    Test suite for the Flask application.

    Usage:
    Run this script directly to execute all test cases using `unittest.main()
    """
    URL = 'http://127.0.0.1:5000'

    def setUp(self):
        """Set up the test client."""
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.test_db_client = MongoClient('mongodb://localhost:27017/')
        self.test_db = self.test_db_client.test_userDB  # Use a separate test database
        self.test_collection = self.test_db.test_userCollection  # Use a separate test collection

    def tearDown(self):
        # Clean up the test database after each test
        self.test_db_client.drop_database('test_userDB')

    def test_total_spent_successful(self):
        """Test successful retrieval of total spending"""

        user_id = 35
        response = self.app.get(f'{self.URL}/total_spent?user_id={user_id}')
        response_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)

        # Assert that the required keys are present in the response
        self.assertIn('user_id', response_data)
        self.assertIn('name', response_data)
        self.assertIn('age', response_data)
        self.assertIn('total_spending', response_data)

    def test_total_spent_missing_user_id(self):
        """Test when user_id parameter is missing"""

        response = self.app.get(f'{self.URL}/total_spent')
        response_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Missing user_id parameter')

    def test_total_spent_user_not_found(self):
        """Test when user is not found"""

        non_existent_user_id = 4000
        response = self.app.get(f'{self.URL}/total_spent?user_id={non_existent_user_id}')
        response_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'User not found')

    def test_average_spending_successful(self):
        """Test successful calculation of average spending"""

        user_id = 445
        response = self.app.get(f'{self.URL}/average_spending_by_age/{user_id}')
        response_data = json.loads(response.data.decode('utf-8'))

        self.assertEqual(response.status_code, 200)

        # Assert that the required keys are present in the response
        self.assertIn('user_id', response_data)
        self.assertIn('age', response_data)
        self.assertIn('average_spending', response_data)
        self.assertIn('age_group', response_data)

    def test_average_spending_user_not_found(self):
        """Test when user is not found"""

        non_existent_user_id = 0
        response = self.app.get(f'{self.URL}/average_spending_by_age/{non_existent_user_id}')
        self.assertEqual(response.status_code, 404)

    def test_write_to_mongodb_successful(self):
        """Test successful data insertion"""

        data = {"user_id": 444, "total_spending": 2600}
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

    def test_get_all_users(self):
        """Test the get_all_users endpoint"""

        expected_user_count = 3000

        response = self.app.get(f'{self.URL}/users')

        # Check status code
        self.assertEqual(response.status_code, 200)

        # Check response data
        response_data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(response_data, dict)

        users = response_data.get('users', [])
        self.assertIsInstance(users, list)

        self.assertEqual(len(users), expected_user_count)

        expected_user_keys = ['user_id', 'name', 'email', 'age']
        for user in users:
            self.assertIsInstance(user, dict)
            for key in expected_user_keys:
                self.assertIn(key, user)

    def test_get_user_by_id_successful(self):
        """Test successful retrieval of a user by ID"""

        user_id = 35
        response = self.app.get(f'{self.URL}/users/{user_id}')
        self.assertEqual(response.status_code, 200)

        # Check response data
        user_data = json.loads(response.data.decode('utf-8'))
        self.assertIsInstance(user_data, dict)

        expected_user_keys = ['user_id', 'name', 'email', 'age']
        for key in expected_user_keys:
            self.assertIn(key, user_data)

    def test_get_user_by_id_not_found(self):
        """Test when user is not found by ID"""

        non_existent_user_id = 3001
        response = self.app.get(f'{self.URL}/users/{non_existent_user_id}')
        self.assertEqual(response.status_code, 404)

        # Check error message
        error_data = json.loads(response.data.decode('utf-8'))
        self.assertIn('error', error_data)
        self.assertEqual(error_data['error'], 'User not found')

    def test_get_mongodb_users_success(self):
        """Test successful retrival of mongodb users"""

        user_data = [{'_id': 1, 'name': 'User1'}, {'_id': 2, 'name': 'User2'}]
        self.test_collection.insert_many(user_data)

        response = self.app.get('/mongodb_users')

        self.assertEqual(response.status_code, 200)

        data = json.loads(response.get_data(as_text=True))

        self.assertIn('mongodb_users', data)


if __name__ == '__main__':
    unittest.main()
