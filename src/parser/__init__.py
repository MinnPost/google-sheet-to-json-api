from flask import Blueprint

bp = Blueprint('parser', __name__)

from src.parser import routes
