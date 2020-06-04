import os
from pathlib import Path
import sys

sys.path.append('../')
from orm.elastic_client import FoodElasticClient
from orm.mongo_client import FoodMongoClient

DATABASE_NAME = "food"

RABBIT_PORT = 8081
RABBIT_QUEUE_NAME = 'alerts'
RABBIT_LOGIN = 'guest'
RABBIT_PASSWORD = 'guest'

REDIS_PORT = 6379

if os.environ.get("DOCKER") == "true":
    MODELS_PATH = Path("./models_storage")
    LOG_PATH = Path("./logs")
    LOG_CONFIG = "./logging.ini"
    WEB_PATH = Path("./templates/web")
    MONGODB_CONNECTION = FoodMongoClient("mongodb", 27017, DATABASE_NAME)
    ELASTICSEARCH_CONNECTION = FoodElasticClient(MONGODB_CONNECTION, "elastic", 9200, "food", "previews") # TODO add docker image
    RABBIT_HOST = 'rabbit'
    REDIS_HOST = 'redis'
else:
    MODELS_PATH = Path("models/")
    LOG_PATH = Path("logs/")
    LOG_CONFIG = "logging.ini"
    WEB_PATH = Path("./templates/web")
    MONGODB_CONNECTION = FoodMongoClient("localhost", 27017, DATABASE_NAME)
    ELASTICSEARCH_CONNECTION = FoodElasticClient(MONGODB_CONNECTION, "elastic", 9200, "food", "previews")
    RABBIT_HOST = 'localhost'

from flask_sqlalchemy import SQLAlchemy

SQLITE_DB = SQLAlchemy()

PHONE_NUMBER = "+79992016933"
BILL_PASS = "929759"

if not LOG_PATH.exists():
    LOG_PATH.mkdir(parents=True)