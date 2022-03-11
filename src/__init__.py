import os
from flask import Flask, jsonify, current_app

from src.extensions import register_extensions

from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    register_extensions(app)

    #from src.errors import bp as errors_bp
    #app.register_blueprint(errors_bp)

    from src.authorize import bp as authorize_bp
    app.register_blueprint(authorize_bp, url_prefix='/authorize')

    from src.parser import bp as parser_bp
    app.register_blueprint(parser_bp, url_prefix='/parser')

    return app

from src import spreadsheet
