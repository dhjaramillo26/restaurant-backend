from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        # description puede ser string o dict (de marshmallow)
        description = error.description
        if isinstance(description, dict):
            description = str(description)
        return jsonify({"error": description}), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        # Esto es solo para debug. En producción puedes omitir el print.
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500
