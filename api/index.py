"""
Vercel serverless function entry point for Flask app
Proper WSGI handler for Vercel's Python runtime
"""
import sys
import os

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Change working directory to project root (critical for file paths)
os.chdir(parent_dir)

# Import Flask app - wrap in try/except to show errors
try:
    from app import app
    
    # Vercel Python runtime expects a handler function or WSGI app
    # The @vercel/python builder can handle Flask apps directly
    # Export as 'handler' for Vercel
    handler = app
    
except Exception as e:
    # Create error handler that shows the actual error
    from flask import Flask
    import traceback
    
    error_app = Flask(__name__)
    
    @error_app.route('/', defaults={'path': ''})
    @error_app.route('/<path:path>')
    def error_handler(path):
        error_details = traceback.format_exc()
        return f"""
        <h1>Application Error</h1>
        <p><strong>Error:</strong> {str(e)}</p>
        <h3>Traceback:</h3>
        <pre>{error_details}</pre>
        <p>Check Vercel function logs for more details.</p>
        """, 500
    
    handler = error_app
