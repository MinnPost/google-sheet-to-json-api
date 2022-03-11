from flask import Blueprint

bp = Blueprint('authorize', __name__)

from src.authorize import routes
