# API Documentation

## Documentation Example

`GET '/api/v1.0/categories'`

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

## API Endpoints

`GET '/categories'`

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

`GET '/questions'`

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

`DELETE '/questions/<int:question_id>'`

- Deletes a question by id.
- Request Arguments: `question_id` (path param, required)
- Returns: `success`, `deleted` (id).

```json
{
  "success": true,
  "deleted": 1
}
```

`POST '/questions'`

- Creates a new question.
- Request Body (JSON): `question` (string, required), `answer` (string, required), `category` (int, required), `difficulty` (int 1-5, required)
- Returns: `success`, `created` (new question id).

```json
{
  "success": true,
  "created": 24
}
```

`PUT '/questions/<int:question_id>'`

- Updates an existing question by id.
- Request Arguments: `question_id` (path param, required)
- Request Body (JSON): any of `question` (string), `answer` (string), `category` (int), `difficulty` (int 1-5)
- Returns: `success`, `updated` (id), `question` (updated question)

```json
{
  "success": true,
  "updated": 24,
  "question": {
    "id": 24,
    "question": "Updated question?",
    "answer": "Updated answer",
    "category": 1,
    "difficulty": 3
  }
}
```

`POST '/questions/search'`

- Searches for questions that contain the given search term (case-insensitive).
- Request Body (JSON): `searchTerm` (string, required)
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

`GET '/categories/<int:category_id>/questions'`

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

`POST '/quizzes'`

- Fetches a random question for the quiz, filtered by category and excluding previous questions.
- Request Body (JSON): `previous_questions` (list of int, required), `quiz_category` (string/int, required). Use `"0"` or `0` for all categories.
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

## Error Handling

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
