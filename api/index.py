"""
Vercel serverless function entry point for Flask app
This handles the WSGI conversion for Vercel's serverless environment
"""
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Change to project root directory (Vercel runs from api/ directory)
os.chdir(parent_dir)

# Import the Flask app from app.py
try:
    from app import app
except Exception as e:
    # If import fails, create a simple error handler
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Error loading app: {str(e)}", 500

# Vercel Python runtime expects the app directly
# The @vercel/python builder handles WSGI conversion automatically
handler = app
