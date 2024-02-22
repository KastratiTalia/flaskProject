import unittest
from app import app

class TestProject(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_hello_world(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.decode('utf-8'), 'Hello, World!')

    def test_get_user(self):
        response = self.app.get('/users/<int:user_id>')



if __name__ == '__main__':
    unittest.main()