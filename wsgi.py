from a2wsgi import ASGIMiddleware
from main import app as app_fastapi

# PythonAnywhere looks for a variable named 'application' by default
application = ASGIMiddleware(app_fastapi)
