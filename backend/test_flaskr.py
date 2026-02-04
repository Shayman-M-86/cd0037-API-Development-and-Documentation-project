import os
import unittest

from flaskr import create_app
from models import db, Question, Category

from config import Config


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.database_path = Config(testing=True).SQLALCHEMY_DATABASE_URI

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.rollback()
            db.session.commit()
    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_cors_headers_are_present_on_get(self):
        res = self.client.get("/categories")  # any existing GET endpoint is fine
        self.assertEqual(res.status_code, 200)

        # after_request headers
        self.assertIn("Access-Control-Allow-Headers", res.headers)
        self.assertIn("Access-Control-Allow-Methods", res.headers)
        
    def test_cors_preflight_options_has_allow_methods(self):
        res = self.client.options(
            "/categories",
            headers={
                "Origin": "http://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Many apps return 200 or 204 for OPTIONS — accept either
        self.assertIn(res.status_code, [200, 204])
        self.assertIn("Access-Control-Allow-Methods", res.headers)
        self.assertIn("GET", res.headers["Access-Control-Allow-Methods"])
        
    
    def test_get_categories(self):
        with self.app.app_context():
            res = self.client.get('/categories')
            data = res.get_json()
            
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['categories'])





# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
