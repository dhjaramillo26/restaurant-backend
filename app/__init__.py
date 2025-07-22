from flask import Flask
from .extensions import db, ma, migrate
from .routes.restaurants import restaurants_bp
from .routes.reservations import reservations_bp
from config import DevConfig
from .error_handlers import register_error_handlers
from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(DevConfig)

    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(restaurants_bp)
    app.register_blueprint(reservations_bp)

    register_error_handlers(app)

    @app.route('/')
    def hello():
        return {"message": "API de Reservas funcionando"}

    return app