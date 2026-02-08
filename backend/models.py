from typing import Optional

from flask import abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from config import ProductionConfig

production_database_path: str = ProductionConfig(testing=False).SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()


def setup_db(app, database_path=production_database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)


class Question(db.Model):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
            "difficulty": self.difficulty,
        }


class Category(db.Model):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {"id": self.id, "type": self.type}


class AppError(Exception):
    status_code = 400
    code = "APP_ERROR"

    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        status_code: Optional[int] = None,
    ):
        super().__init__(message)
        if code:
            self.code = code
        if status_code:
            self.status_code = status_code


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class ValidationError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


class QuestionCreationValidation:
    def __init__(self, question, answer, category, difficulty) -> None:
        try:
            self.difficulty = self.validate_difficulty(difficulty)
            self.category = self.validate_category(category)
            self.question = self.validate_question(question)
            self.answer = self.validate_answer(answer)
        except ValueError as e:
            abort(400, description=str(e.args[0]))

    @staticmethod
    def validate_difficulty(difficulty) -> int:
        try:
            difficulty = int(difficulty)
        except (TypeError, ValueError):
            raise ValidationError(
                "difficulty must be an integer between 1 and 5", status_code=422
            ) from None
        if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 5:
            raise ValidationError(
                "difficulty must be an integer between 1 and 5", status_code=422
            ) from None
        return difficulty

    @staticmethod
    def validate_category(category_id: int) -> int:
        try:
            category_id = int(category_id)
        except (TypeError, ValueError):
            raise ValidationError(
                "category must be a positive integer", status_code=422
            ) from None

        if not isinstance(category_id, int) or category_id < 1:
            raise ValidationError(
                "category must be a positive integer", status_code=422
            ) from None

        if not db.session.get(Category, category_id):
            raise ValidationError(
                f"Category with id {category_id} does not exist", status_code=422
            ) from None

        return category_id

    @staticmethod
    def validate_answer(answer: str) -> str:
        if not isinstance(answer, str) or not answer.strip():
            raise ValidationError(
                "answer must be a non-empty string", status_code=422
            ) from None
        return answer.strip()

    @staticmethod
    def validate_question(question: str) -> str:
        if not isinstance(question, str) or not question.strip():
            raise ValidationError(
                "question must be a non-empty string", status_code=422
            ) from None
        return question.strip()
