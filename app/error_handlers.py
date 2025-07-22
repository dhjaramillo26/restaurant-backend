"""Centralized error handlers for the API."""

from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register handlers for HTTP and generic exceptions."""
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Return JSON for known HTTP exceptions."""

        description = error.description
        if isinstance(description, dict):
            description = str(description)
        return jsonify({"error": description}), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Return a generic 500 error in JSON format."""

        import traceback
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500
