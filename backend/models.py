from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import UniqueConstraint, Integer, String
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
from flask import abort


from config import ProductionConfig




production_database_path: str = ProductionConfig(testing=False).SQLALCHEMY_DATABASE_URI

db = SQLAlchemy()

def setup_db(app, database_path=production_database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)


class Question(db.Model):
    __tablename__ = 'questions'

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
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }

class QuestionValidation:
    
    def __init__(self, question, answer, category, difficulty) -> None:
        try:
            self.difficulty = self.validate_difficulty(difficulty)
            self.category = self.validate_category(category)
            self.question = self.validate_question(question)
            self.answer = self.validate_answer(answer)
        except ValueError as e:
            abort(400, description=str(e.args[0]))

    
    @staticmethod
    def validate_difficulty(difficulty: int) -> int:
        if not isinstance(difficulty, int) or difficulty < 1 or difficulty > 5:
            raise ValueError("difficulty must be an integer between 1 and 5")
        return difficulty
    
    @staticmethod
    def validate_category(category_id: int) -> int:
        if not isinstance(category_id, int) or category_id < 1:
            raise ValueError("category must be a positive integer")
        if not db.session.get(Category, category_id):
            raise ValueError(f"Category with id {category_id} does not exist")
        return category_id
    
    @staticmethod
    def validate_answer(answer: str) -> str:
        if not isinstance(answer, str) or not answer.strip():
            raise ValueError("answer must be a non-empty string")
        return answer.strip()
    
    @staticmethod
    def validate_question(question: str) -> str:
        if not isinstance(question, str) or not question.strip():
            raise ValueError("question must be a non-empty string")
        return question.strip()


class Category(db.Model):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
