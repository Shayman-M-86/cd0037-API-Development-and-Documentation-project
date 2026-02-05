import logging
import unittest

from sqlalchemy import text

from config import AppTestingConfig
from flaskr import create_app
from models import Category, Question, db

logging.basicConfig(level=logging.INFO)


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""

        self.database_path: str = AppTestingConfig(testing=True).SQLALCHEMY_DATABASE_URI

        self.app = create_app(
            {
                "SQLALCHEMY_DATABASE_URI": self.database_path,
                "SQLALCHEMY_TRACK_MODIFICATIONS": False,
                "TESTING": True,
            }
        )
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            with open("trivia_test_sqlalchemy.psql", "r", encoding="utf-8") as f:
                sql = f.read()
            db.session.execute(text(sql))
            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.session.rollback()
            Question.query.delete()
            Category.query.delete()
            db.session.commit()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_cors_headers_are_present_on_get(self):
        res = self.client.get("/categories")
        self.assertEqual(res.status_code, 200)

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

        self.assertIn(res.status_code, [200, 204])
        self.assertIn("Access-Control-Allow-Methods", res.headers)
        self.assertIn("GET", res.headers["Access-Control-Allow-Methods"])

    def test_get_categories(self):
        with self.app.app_context():
            res = self.client.get("/categories")
            data = res.get_json()

            self.assertEqual(res.status_code, 200)
            self.assertTrue(data["categories"])

    def test_get_questions(self):
        EXPECTED_KEYS = {"id", "question", "answer", "category", "difficulty"}
        with self.app.app_context():
            for i in range(2):
                res = self.client.get("/questions", query_string={"page": i + 1})
                data = res.get_json()

                self.assertEqual(res.status_code, 200)
                self.assertTrue(data["questions"])
                self.assertLessEqual(len(data["questions"]), 10)
                self.assertTrue(data["total_questions"])
                self.assertTrue(len(data["categories"]))
                self.assertIsNone(data["current_category"])
                self.assertTrue(data["questions"])

                for question in data["questions"]:
                    self.assertIsInstance(question, dict)
                    self.assertEqual(set(question.keys()), EXPECTED_KEYS)

    def test_delete_question(self):
        with self.app.app_context():
            category = Category(type="Test Category")
            db.session.add(category)
            db.session.commit()

            question = Question(
                question="Delete me?",
                answer="Yes",
                category=category.id,
                difficulty=1,
            )
            db.session.add(question)
            db.session.commit()

            question_id = question.id

        res = self.client.delete(f"/questions/{question_id}")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertEqual(data["deleted"], question_id)

        with self.app.app_context():
            deleted_question = db.session.get(Question, question_id)
            self.assertIsNone(deleted_question)

        res = self.client.get("/questions")
        data = res.get_json()

        ids = [q["id"] for q in data["questions"]]
        self.assertNotIn(question_id, ids)

    def test_questions_post(self):
        new_question = {
            "question": "What is the capital of France?",
            "answer": "Paris",
            "category": 3,
            "difficulty": 2,
        }

        res = self.client.post("/questions", json=new_question)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["created"])

        created_question_id = data["created"]

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
            "difficulty": 10,  # Invalid difficulty
        }

        res = self.client.post("/questions", json=invalid_question)
        data = res.get_json()

        self.assertEqual(res.status_code, 422)
        self.assertFalse(data["success"])
        self.assertIn("difficulty must be an integer between 1 and 5", data["message"])

    def test_search_questions_by_term(self):
        payload = {"searchTerm": "title"}

        res = self.client.post("/questions/search", json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])
        self.assertGreater(len(data["questions"]), 0)

        for question in data["questions"]:
            self.assertIn("title", question["question"].lower())

    def test_get_questions_by_category(self):
        category_id = 1

        res = self.client.get(f"/categories/{category_id}/questions")
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["success"])
        self.assertTrue(data["questions"])
        self.assertGreater(len(data["questions"]), 0)

        for q in data["questions"]:
            self.assertEqual(q["category"], category_id)

    def test_quizzes_returns_question(self):
        payload = {
            "previous_questions": [],
            "quiz_category": "0",
        }

        res = self.client.post("/quizzes", json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertIn("question", data)
        self.assertIsInstance(data["question"], dict)

        q = data["question"]
        self.assertIn("id", q)
        self.assertIn("question", q)
        self.assertIn("answer", q)
        self.assertIn("difficulty", q)
        self.assertIn("category", q)

    def test_quizzes_excludes_previous_questions(self):
        previous = [1, 4, 20, 15]
        payload = {"previous_questions": previous, "quiz_category": "0"}

        res = self.client.post("/quizzes", json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
        self.assertNotIn(data["question"]["id"], previous)

    def test_quizzes_filters_by_category(self):
        category_id = "4"

        payload = {"previous_questions": [], "quiz_category": category_id}

        res = self.client.post("/quizzes", json=payload)
        data = res.get_json()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data["question"])
        self.assertEqual(str(data["question"]["category"]), category_id)


if __name__ == "__main__":
    unittest.main()
