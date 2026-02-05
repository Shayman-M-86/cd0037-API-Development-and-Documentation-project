from flask import Request, abort

from models import Category


def get_pagination(request: Request, PAGE_SIZE=10) -> tuple[int, int, int]:
    page = request.args.get("page", default=1, type=int)

    if page < 1:
        abort(400, description="page must be >= 1")

    offset = (page - 1) * PAGE_SIZE
    return page, PAGE_SIZE, offset


def validate_categories(categories) -> list[Category]:
    if not isinstance(categories, list):
        abort(400, description="categories is not a list")

    for category in categories:
        if not isinstance(category.id, int) or not isinstance(category.type, str):
            abort(400, description="category id must be int and type must be str")

    return categories


def validate_category_id(category_id: int) -> int:
    if not isinstance(category_id, int) or category_id < 1:
        abort(400, description="category_id must be a positive integer")
    return category_id


def validate_question_id(question_id: int) -> int:
    if not question_id:
        abort(400, description="question_id is required")
    if not isinstance(question_id, int) or question_id < 1:
        abort(400, description="question_id must be a positive integer")
    return question_id
