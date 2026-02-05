import os
import unittest
from sqlalchemy import text
import logging

from flaskr import create_app
from models import db, Question, Category

from config import AppTestingConfig

logging.basicConfig(level=logging.INFO)
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.database_path: str = AppTestingConfig(testing=True).SQLALCHEMY_DATABASE_URI

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            sql = open("trivia_test_sqlalchemy.psql", "r", encoding="utf-8").read()
            db.session.execute(text(sql))
            db.session.commit()
            
        
        

    def tearDown(self):
        with self.app.app_context():
            db.session.rollback()
            # Question.query.delete()
            # Category.query.delete()
            # db.session.commit()
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
            
    
    def test_get_questions(self):
        EXPECTED_KEYS = {"id", "question", "answer", "category", "difficulty"}
        with self.app.app_context():
            for i in range(2):

                res = self.client.get('/questions', query_string={'page': i+1})
                data = res.get_json()
                
                self.assertEqual(res.status_code, 200)
                self.assertTrue(data['questions'])
                self.assertLessEqual(len(data['questions']), 10)
                self.assertTrue(data['total_questions'])
                self.assertTrue(len(data['categories']))
                self.assertIsNone(data['current_category'])
                self.assertTrue(data["questions"])
                
                for question in data["questions"]:
                    self.assertIsInstance(question, dict)
                    self.assertEqual(set(question.keys()), EXPECTED_KEYS)

    def test_delete_question(self):
        with self.app.app_context():
            # Create a category
            category = Category(type="Test Category")
            db.session.add(category)
            db.session.commit()

            # Create a question to delete
            question = Question(
                question="Delete me?",
                answer="Yes",
                category=category.id,
                difficulty=1,
            )
            db.session.add(question)
            db.session.commit()

            question_id = question.id

        # Delete the question
        res = self.client.delete(f"/questions/{question_id}")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], question_id)

        # Verify it is removed from the database
        with self.app.app_context():
            deleted_question = db.session.get(Question, question_id)
            self.assertIsNone(deleted_question)

        # Verify refresh does not bring it back
        res = self.client.get("/questions")
        data = res.get_json()

        ids = [q["id"] for q in data["questions"]]
        self.assertNotIn(question_id, ids)
    
    
    def test_questions_post(self):
        new_question = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "category": 3,
            "difficulty": 2
        }

        res = self.client.post("/questions", json=new_question)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["created"])

        created_question_id = data["created"]

        # Verify the question exists in the database
        with self.app.app_context():
            question: Question = db.session.get(Question, created_question_id)  # type: ignore
            self.assertIsNotNone(question)
            self.assertEqual(question.question, new_question["question"])
            self.assertEqual(question.answer, new_question["answer"])
            self.assertEqual(question.category, new_question["category"])
            self.assertEqual(question.difficulty, new_question["difficulty"])
    
    def test_questions_post_invalid_data(self):
        invalid_question = {
            "question": "",
            "answer": "Paris",
            "category": 3,
            "difficulty": 10  # Invalid difficulty
        }

        res = self.client.post("/questions", json=invalid_question)
        data = res.get_json()

        self.assertEqual(res.status_code, 400)
        self.assertFalse(data["success"])
        self.assertIn("difficulty must be an integer between 1 and 5", data["message"])



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
