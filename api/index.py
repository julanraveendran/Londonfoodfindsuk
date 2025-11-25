"""
Vercel serverless function entry point for Flask app
"""
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app from app.py
from app import app

# Vercel expects a 'handler' variable that is the WSGI app
# For Vercel Python runtime, we can export the Flask app directly
handler = app
