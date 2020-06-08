import os
import sys
from pathlib import Path

from sources.edimdoma.loader import EdimDoma

sys.path.append('../')
from orm.elastic_client import FoodElasticClient
from orm.mongo_client import FoodMongoClient
from alerts.alert import alert

DATABASE_NAME = "food"

RABBIT_PORT = 5672
RABBIT_QUEUE_NAME = 'crawler-errors'
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
    RABBIT_HOST = 'rabbitmq'
else:
    BASE_PATH = Path("../database/")
    LOG_PATH = Path("../logs")
    LOG_CONFIG = Path("../logging.ini")
    MONGODB_CONNECTION = FoodMongoClient("localhost", 27017, DATABASE_NAME)
    ELASTICSEARCH_CONNECTION = FoodElasticClient(MONGODB_CONNECTION, "elastic", 9200, "food", "previews")
    RABBIT_HOST = 'localhost'

ALERT_SETTINGS = dict(
    host=RABBIT_HOST,
    port=RABBIT_PORT,
    login=RABBIT_LOGIN,
    password=RABBIT_PASSWORD,
    queue_name=RABBIT_QUEUE_NAME
)

ALERT_FUNCTION = alert

if not LOG_PATH.exists():
    LOG_PATH.mkdir(parents=True)

DATA_SOURCES = dict(
    edimdoma=EdimDoma,
)
