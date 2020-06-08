import os
import sys
from pathlib import Path

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
    BASE_PATH = Path("../database")
    LOG_PATH = Path("./logs")
    LOG_CONFIG = "./logging.ini"
    MONGODB_CONNECTION = FoodMongoClient("mongodb", 27017, DATABASE_NAME)
    ELASTICSEARCH_CONNECTION = FoodElasticClient(MONGODB_CONNECTION, "elastic", 9200, "food",
                                                 "previews")  # TODO add docker image
    RABBIT_HOST = 'rabbit'
else:
    BASE_PATH = Path("../database/")
    LOG_PATH = Path("../logs")
    LOG_CONFIG = Path("../logging.ini")
    MONGODB_CONNECTION = FoodMongoClient("localhost", 27017, DATABASE_NAME)
    ELASTICSEARCH_CONNECTION = FoodElasticClient(MONGODB_CONNECTION, "elastic", 9200, "food", "previews")
    RABBIT_HOST = 'localhost'

ALERT_SETTINGS = dict(
    host=RABBIT_HOST,
    port=REDIS_PORT,
    login=RABBIT_LOGIN,
    password=RABBIT_PASSWORD,
    queue_name=RABBIT_QUEUE_NAME
)

if not LOG_PATH.exists():
    LOG_PATH.mkdir(parents=True)
