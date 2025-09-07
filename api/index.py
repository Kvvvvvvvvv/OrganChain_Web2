import sys
import os

# Add the server directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'server'))

# Import the Flask app
from app import app

# Vercel serverless function handler
def handler(request):
    return app(request.environ, start_response)

def start_response(status, headers):
    pass

# For Vercel compatibility
if __name__ == "__main__":
    app.run()
