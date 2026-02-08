# Backend - Trivia API

## Requirements

- Python 3.9.25
- Postgres

## Environment Variables

Secrets are loaded from environment variables via `python-dotenv`. Create a `.env` file (see `.env.example`) with the following values:

- `DATABASE_URL` (production DB)
- `SECRET_KEY`
- `TEST_DATABASE_URL` (must include the word `test`)
- `TEST_SECRET_KEY`

---

## Install Dependencies

This project requires Python 3.9.25 for compatibility.

### UV Guide

1. Install Python 3.9.25.
2. `cd` into the backend project directory.
3. Create and activate a virtual environment.

    ```bash
    uv venv .venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        source .venv\Scripts\activate
        ```

    - On Unix or MacOS:

        ```bash
        source .venv/bin/activate
        ```

5. Install dependencies with UV:

    ```bash
    uv sync
    ```

### Pip Guide

1. Install Python 3.9.25.
2. `cd` into the backend project directory.
3. Create a virtual environment:

    ```bash
    python -m venv .venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        source .venv\Scripts\activate
        ```

    - On Unix or MacOS:

        ```bash
        source .venv/bin/activate
        ```

5. Install dependencies with pip:

```bash
pip install -r requirements.txt
```

---

## Set up the Database

With Postgres running, create a `trivia` database:

```bash
createdb trivia
```

Populate the database using the `trivia.psql` file provided:

```bash
psql trivia < trivia.psql
```

## Run the Server

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run --reload
```

## Project Notes

These are the files you'd want to edit in the backend:

1. `backend/flaskr/__init__.py`
2. `backend/test_flaskr.py`

One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle `GET` requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle `GET` requests for all available categories.
4. Create an endpoint to `DELETE` a question using a question `ID`.
5. Create an endpoint to `POST` a new question, which will require the question and answer text, category, and difficulty score.
6. Create a `POST` endpoint to get questions based on category.
7. Create a `POST` endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a `POST` endpoint to get questions to play the quiz. This endpoint should take a category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422, and 500.

## API Documentation

Detailed endpoint documentation is included below and in `API_DOCUMENTATION.md`. Each entry includes the METHOD, URL, request parameters, and response body.

### Documentation Example

`GET '/categories'`

- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, `categories`, that contains an object of `id: category_string` key: value pairs.

```json
{
  "1": "Science",
  "2": "Art",
  "3": "Geography",
  "4": "History",
  "5": "Entertainment",
  "6": "Sports"
}
```

### API Endpoints

#### `GET '/categories'`

- Fetches a dictionary of all categories.
- Request Arguments: None
- Returns: `success`, `categories` where `categories` is an object of `id: category_string` pairs.

```json
{
  "success": true,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  }
}
```

---

#### `GET '/questions'`

- Fetches a paginated list of questions (10 per page), categories, and total question count.
- Request Arguments (Query Params): `page` (optional, int, default `1`)
- Returns: `success`, `questions`, `total_questions`, `categories`, `current_category` (`null`).

```json
{
  "success": true,
  "questions": [
    {
      "id": 1,
      "question": "This is a question",
      "answer": "This is an answer",
      "category": 2,
      "difficulty": 1
    }
  ],
  "total_questions": 19,
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports"
  },
  "current_category": null
}
```

---

#### `DELETE '/questions/<int:question_id>'`

- Deletes a question by id.
- Request Arguments: `question_id` (path param, required)
- Returns: `success`, `deleted` (id).

```json
{
  "success": true,
  "deleted": 1
}
```

---

#### `POST '/questions'`

- Creates a new question.
- Request Body (JSON): `question` (string, required), `answer` (string, required), `category` (int, required), `difficulty` (int 1-5, required)

```json
{
  "question": "Which planet is known as the Red Planet?",
  "answer": "Mars",
  "category": 1,
  "difficulty": 2
}
```

- Returns: `success`, `created` (new question id).

```json
{
  "success": true,
  "created": 24
}
```

---

#### `POST '/questions/search'`

- Searches for questions that contain the given search term (case-insensitive).
- Request Body (JSON): `searchTerm` (string, required)

```json
{ "searchTerm": "Shakespeare" }
```

- Returns: `success`, `questions`, `total_questions`, `current_category` (`null`).

```json
{
  "success": true,
  "questions": [
    {
      "id": 4,
      "question": "Which Shakespeare play features the question, 'To be or not to be'?",
      "answer": "Hamlet",
      "category": 4,
      "difficulty": 2
    }
  ],
  "total_questions": 1,
  "current_category": null
}
```

---

#### `GET '/categories/<int:category_id>/questions'`

- Fetches questions for a specific category.
- Request Arguments: `category_id` (path param, required)
- Returns: `success`, `questions`, `total_questions`, `current_category` (category id).

```json
{
  "success": true,
  "questions": [
    {
      "id": 3,
      "question": "This is a question",
      "answer": "This is an answer",
      "category": 1,
      "difficulty": 2
    }
  ],
  "total_questions": 5,
  "current_category": 1
}
```

---

#### `POST '/quizzes'`

- Fetches a random question for the quiz, filtered by category and excluding previous questions.
- Request Body (JSON): `previous_questions` (list of int, required), `quiz_category` (string/int, required). Use `"0"` or `0` for all categories.

```json
{
  "previous_questions": [5, 9, 12],
  "quiz_category": "3"
}
```

- Returns: `question` (object) or `null` when no more questions are available.

```json
{
  "question": {
    "id": 9,
    "question": "What is the heaviest organ in the human body?",
    "answer": "The liver",
    "category": 1,
    "difficulty": 4
  }
}
```

```json
{
  "question": null
}
```

---

### Error Handling

Errors are returned as JSON in the following format:

```json
{
  "success": false,
  "error": 404,
  "message": "Resource not found"
}
```

The API returns the following error types:

- `400` - Bad Request (invalid inputs or missing required fields)
- `404` - Resource Not Found
- `422` - Unprocessable Entity (validation or delete errors)
- `500` - Internal Server Error

## Testing

Write at least one test for the success and at least one error behavior of each endpoint using the unittest library.

To deploy the tests, run

```bash
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
