import os
from pathlib import Path

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    BASE_DIR = Path(__file__).parent.parent
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_BUCKET = os.environ.get("AWS_BUCKET", "")
    AWS_FOLDER = os.path.join(os.environ.get("AWS_FOLDER", ""), '') # make sure it has one slash and only one slash
    CACHE_TYPE = os.environ.get("CACHE_TYPE", "redis")
    CACHE_REDIS_HOST = os.environ.get("CACHE_REDIS_HOST", "redis")
    CACHE_REDIS_PORT = os.environ.get("CACHE_REDIS_PORT", 6379)
    CACHE_REDIS_DB = os.environ.get("CACHE_REDIS_DB", 0)
    CACHE_REDIS_URL = os.environ.get("CACHE_REDIS_URL", "redis://127.0.0.1:6379/0")
    CACHE_DEFAULT_TIMEOUT = os.environ.get("CACHE_DEFAULT_TIMEOUT", 500)
    S3_DOMAIN_ROOT = os.path.join(os.environ.get("S3_DOMAIN_ROOT", "https://s3.amazonaws.com/"), '') # make sure it has one slash and only one slash
    USE_AWS_S3 = os.environ.get("USE_AWS_S3", "false").lower()
    WORKSHEET_NAME_SEPARATOR = os.environ.get("WORKSHEET_NAME_SEPARATOR", "|")
