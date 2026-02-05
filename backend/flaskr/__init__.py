import random
from typing import Optional, cast

from flask import Flask, Response, abort, jsonify, request
from flask.typing import ResponseReturnValue
from flask_cors import CORS
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from models import Category, Question, QuestionValidation, ValidationError, db, setup_db

from .route_helpers import (
    get_pagination,
    validate_categories,
    validate_category_id,
    validate_question_id,
)

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get("SQLALCHEMY_DATABASE_URI")
        setup_db(app, database_path=database_path)

    # @TODO: Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    # @TODO: Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response: Response) -> Response:
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    
    """

    @app.route("/categories", methods=["GET"])
    def get_categories():
        try:
            categories: list[Category] = Category.query.order_by(Category.id).all()
        except SQLAlchemyError:
            abort(500, description="Database error while fetching categories.")

        categories = validate_categories(categories)
        categories_dict: dict[int, str] = {c.id: c.type for c in categories}

        return jsonify({"success": True, "categories": categories_dict})

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route("/questions", methods=["GET"])
    def get_questions():
        page, page_size, offset = get_pagination(request, QUESTIONS_PER_PAGE)

        try:
            questions: list[Question] = (
                Question.query.order_by(Question.id)
                .offset(offset)
                .limit(page_size)
                .all()
            )
            total_questions: int = Question.query.count()
            categories: list[Category] = Category.query.order_by(Category.id).all()
        except SQLAlchemyError:
            abort(500, description="Database error while fetching questions.")

        if not questions and page != 1:
            abort(404, description="Page out of range.")

        categories_dict: dict[int, str] = {c.id: c.type for c in categories}

        return jsonify(
            {
                "success": True,
                "questions": [
                    {
                        "id": q.id,
                        "question": q.question,
                        "answer": q.answer,
                        "category": q.category,
                        "difficulty": q.difficulty,
                    }
                    for q in questions
                ],
                "total_questions": total_questions,
                "categories": categories_dict,
                "current_category": None,
            }
        )

    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_question(question_id: int):
        qid: int = validate_question_id(question_id)

        question = db.session.get(Question, qid)
        if not question:
            abort(404, description=f"Question with id {qid} not found.")

        try:
            question.delete()
        except SQLAlchemyError:
            db.session.rollback()
            abort(422, description=f"Unable to delete question with id {qid}.")

        return jsonify({"success": True, "deleted": qid})

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route("/questions", methods=["POST"])
    def add_question():
        body = request.get_json(silent=True)
        if body is None:
            abort(400, description="Request does not contain a valid JSON body.")

        try:
            question_data = QuestionValidation(
                question=body.get("question"),
                answer=body.get("answer"),
                category=body.get("category"),
                difficulty=body.get("difficulty"),
            )

            new_question = Question(
                question=question_data.question,
                answer=question_data.answer,
                category=question_data.category,
                difficulty=question_data.difficulty,
            )
            new_question.insert()

            return jsonify({"success": True, "created": new_question.id})

        except ValidationError as e:
            abort(422, description=str(e))

        except SQLAlchemyError:
            db.session.rollback()
            abort(500, description="Unable to add question, database error.")

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    @app.route("/questions/search", methods=["POST"])
    def search_questions():
        body = request.get_json(silent=True)
        if body is None:
            abort(400, description="Request does not contain a valid JSON body.")

        search_term: Optional[str] = body.get("searchTerm")
        if search_term is None:
            abort(400, description="searchTerm is required in the request body.")

        search_term = search_term.strip()
        if not search_term:
            abort(400, description="searchTerm cannot be empty or whitespace.")

        try:
            questions: list[Question] = (
                db.session.query(Question)
                .filter(Question.question.ilike(f"%{search_term}%"))
                .all()
            )
        except SQLAlchemyError:
            abort(
                500,
                description="Database error occurred while searching for questions.",
            )

        return jsonify(
            {
                "success": True,
                "questions": [q.format() for q in questions],
                "total_questions": len(questions),
                "current_category": None,
            }
        )

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id: int):
        cid = validate_category_id(category_id)

        try:
            category = db.session.get(Category, cid)
        except SQLAlchemyError:
            abort(500, description="Database error while fetching category.")

        if not category:
            abort(404, description=f"Category with id {cid} not found.")

        try:
            questions: list[Question] = (
                db.session.query(Question).filter_by(category=cid).all()
            )
        except SQLAlchemyError:
            abort(500, description="Database error while fetching category questions.")

        return jsonify(
            {
                "success": True,
                "questions": [q.format() for q in questions],
                "total_questions": len(questions),
                "current_category": cid,
            }
        )

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def play_quiz():
        body = request.get_json(silent=True)
        if body is None:
            abort(400, description="Request does not contain a valid JSON body.")

        previous_questions = body.get("previous_questions", [])
        quiz_category = body.get("quiz_category", "0")

        if not isinstance(previous_questions, list) or any(
            not isinstance(x, int) for x in previous_questions
        ):
            abort(400, description="previous_questions must be a list of integers.")

        query = Question.query

        if quiz_category not in ("0", 0, "All", None, ""):
            try:
                category_id = int(quiz_category)
            except (TypeError, ValueError):
                abort(
                    400,
                    description="quiz_category must be a category id (string/int) or '0' for All.",
                )

            try:
                if not db.session.get(Category, category_id):
                    abort(404, description=f"Category with id {category_id} not found.")
            except SQLAlchemyError:
                abort(500, description="Database error while validating category.")

            query = query.filter(Question.category == category_id)

        if previous_questions:
            query = query.filter(~Question.id.in_(previous_questions))

        try:
            available = query.all()
        except SQLAlchemyError:
            abort(500, description="Database error while fetching quiz questions.")

        if not available:
            return jsonify({"question": None}), 200

        question = random.choice(available)
        return jsonify({"question": question.format()}), 200

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    """
    Global Error Handler 
    """

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException) -> ResponseReturnValue:
        status_code = cast(int, err.code or 500)

        return (
            jsonify(
                {
                    "success": False,
                    "error": status_code,
                    "message": err.description if err.description else err.name,
                }
            ),
            status_code,
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(_err: Exception):
        return jsonify(
            {
                "success": False,
                "error": 500,
                "message": "Internal server error",
            }
        ), 500

    return app
