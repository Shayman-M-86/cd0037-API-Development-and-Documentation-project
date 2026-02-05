

echo "Running Flask app"
export FLASK_APP=flaskr
export FLASK_ENV=development
uv run flask run --debug --host 0.0.0.0 --port 5000
