# api-livescore installation
pip install -r requirements.txt
# to run proj
gunicorn --bind 0.0.0.0:8000 wsgi

