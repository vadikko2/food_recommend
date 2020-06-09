import os
import sys
from pathlib import Path

from sources.edimdoma.loader import EdimDoma
from sources.eda.loader import EdaRu

sys.path.append('../')
from core.orm.elastic_client import FoodElasticClient
from core.orm.mongo_client import FoodMongoClient
from core.alerts.alert import alert
from core.logger.logger import Logger

DATABASE_NAME = "food"

REDIS_PORT = 6379

if os.environ.get("DOCKER") == "true":
    BASE_PATH = Path("../database")  # куда сохранять обработанные файлы перед сохранением в базу
    LOG_PATH = Path("./logs")  # папка с логами
    LOG_CONFIG = "./logging.ini"  # конфиг для логов
    MONGODB_CONNECTION = FoodMongoClient("mongodb", 27017, DATABASE_NAME)
    ELASTICSEARCH_CONNECTION = FoodElasticClient(MONGODB_CONNECTION, "elastic", 9200, DATABASE_NAME,
                                                 "previews")  # TODO add docker image
    RABBIT_HOST = 'rabbitmq'
else:
    BASE_PATH = Path("../database/")
    LOG_PATH = Path("./logs")
    LOG_CONFIG = Path("./logging.ini")
    MONGODB_CONNECTION = FoodMongoClient("localhost", 27017, DATABASE_NAME)
    ELASTICSEARCH_CONNECTION = FoodElasticClient(MONGODB_CONNECTION, "elastic", 9200, DATABASE_NAME, "previews")
    RABBIT_HOST = 'localhost'

'''
    Проверка директории с логами
'''
if not LOG_PATH.exists():
    LOG_PATH.mkdir(parents=True)
Logger = Logger
'''
    Насройки для работы с модулем Alerts
'''
RABBIT_PORT = 5672
RABBIT_QUEUE_NAME = 'crawler-errors'
RABBIT_DB_INFO_QUEUE_NAME = 'db-updates'
RABBIT_LOGIN = 'guest'
RABBIT_PASSWORD = 'guest'

ALERT_SETTINGS = dict(
    host=RABBIT_HOST,
    port=RABBIT_PORT,
    login=RABBIT_LOGIN,
    password=RABBIT_PASSWORD,
    queue_name=RABBIT_QUEUE_NAME
)

DB_INFO_ALERT_SETTINGS = dict(
    host=RABBIT_HOST,
    port=RABBIT_PORT,
    login=RABBIT_LOGIN,
    password=RABBIT_PASSWORD,
    queue_name=RABBIT_DB_INFO_QUEUE_NAME
)
ALERT_FUNCTION = alert


'''
    Источники данных
'''
DATA_SOURCES = dict(
    edimdoma=EdimDoma,
    #edaru=EdaRu
)
