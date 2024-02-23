import unittest
import requests
from app import app


class TestProject(unittest.TestCase):
    URL = 'http://127.0.0.1:5000'

    def setUp(self):
        self.app = app.test_client()

    def test_1_get_all_users(self):
        """Test_1: get all users and user count"""
        path = self.URL + '/users'
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(len(data), 3000)
        print("Test 1 completed")



    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello, World!')




if __name__ == '__main__':
    unittest.main()
