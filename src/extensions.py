from src.jwt import jwt
from src.cache import cache
from src.logger import ParserLogger

def register_extensions(app):

    jwt.init_app(app)
    cache.init_app(app)
    
    app.log = ParserLogger('parser_results').logger
