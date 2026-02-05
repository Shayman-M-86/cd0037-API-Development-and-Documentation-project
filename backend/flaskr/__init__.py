

from flask import Flask, request, abort, jsonify, Response
from flask_cors import CORS
import random
from typing import Optional, cast
from models import setup_db, Question, Category, db, QuestionValidation
from .route_helpers import get_pagination , validate_categories, validate_category_id, validate_question_id

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    # @TODO: Set up CORS. Allow '*' for origins.
    CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    # @TODO: Use the after_request decorator to set Access-Control-Allow
    @app.after_request
    def after_request(response: Response) -> Response:
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
        response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,PATCH,DELETE,OPTIONS")
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    
    """
    @app.route('/categories', methods=['GET'])
    def get_categories():

        categories: list[Category] = Category.query.order_by(Category.id).all()
        categories: list[Category] = validate_categories(categories)
        
        categories_dict: dict[int, str] = {category.id: category.type for category in categories}
        


        return jsonify({
            'success': True,
            'categories': categories_dict
        })


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
    @app.route('/questions', methods=['GET'])
    def get_questions():
        page, page_size, offset = get_pagination(request, QUESTIONS_PER_PAGE)

        questions: list[Question] = Question.query.order_by(Question.id).offset(offset).limit(page_size).all()
        total_questions: int = Question.query.count()

        if not questions and page != 1:
            abort(404)

        categories: list[Category] = Category.query.order_by(Category.id).all()
        categories_dict: dict[int, str] = {category.id: category.type for category in categories}


        return jsonify(
            {
                "success": True,
                "questions": [
                    {
                        "id": question.id,
                        "question": question.question,
                        "answer": question.answer,
                        "category": question.category,
                        "difficulty": question.difficulty,
                    }
                    for question in questions
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
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id: int):
        id: int = validate_question_id(question_id)
        question = db.session.get(Question, id)

        if not question:
            abort(404, description=f"Question with id {question_id} not found.")
        question = cast(Question, question)
        
        try:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except Exception:
            db.session.rollback()
            abort(422, description=f"Unable to delete question with id {question_id}.")

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def add_question():
        body: dict = request.get_json()

        if not body:
            abort(400, description="Request does not contain a valid JSON body.")

        question_text = body.get("question")
        answer_text = body.get("answer")
        category = body.get("category")
        difficulty = body.get("difficulty")

        try:
            question_data = QuestionValidation(
                question=question_text,
                answer=answer_text,
                category=category,
                difficulty=difficulty,
            )

            new_question = Question(
                question=question_data.question,
                answer=question_data.answer,
                category=question_data.category,
                difficulty=question_data.difficulty,
            )
            new_question.insert()

            return jsonify({
                "success": True,
                "created": new_question.id,
            })
        except Exception:
            db.session.rollback()
            abort(400, description="Unable to add question.")

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """

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

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """

    return app

