import json
import os
import sys
from pathlib import Path

sys.path.append('../')
from core.orm.elastic_client import FoodElasticClient
from core.orm.mongo_client import FoodMongoClient
from core.alerts.alert import alert
from core.logger.logger import Logger


DATABASE_NAME = "food"

REDIS_PORT = 6379

if os.environ.get("DOCKER") == "true":
    MODELS_PATH = Path("./models_storage")

    LOG_PATH = Path("./logs")
    LOG_CONFIG = "./logging.ini"

    WEB_PATH = Path("./templates/web")

    MONGO_HOST = "mongodb"
    ELASTICSEARCH_HOST = "elasticsearch"
    RABBIT_HOST = 'rabbitmq'
    REDIS_HOST = 'redis'
else:
    MODELS_PATH = Path("models_storage/")

    LOG_PATH = Path("logs/")
    LOG_CONFIG = "logging.ini"

    WEB_PATH = Path("./templates/web")

    MONGO_HOST = "localhost"
    ELASTICSEARCH_HOST = "localhost"
    RABBIT_HOST = 'localhost'
    REDIS_HOST = 'localhost'

'''
    Насройки для работы с модулем Alerts
'''
RABBIT_PORT = 5672
RABBIT_QUEUE_NAME = 'api-errors'
RABBIT_NEW_USERS_QUEUE_NAME = 'new-users'
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
    queue_name=RABBIT_NEW_USERS_QUEUE_NAME
)

ALERT_FUNCTION = alert

'''
    Проверка директории с логами
'''
if not LOG_PATH.exists():
    LOG_PATH.mkdir(parents=True)
Logger = Logger

'''
    Sqlite база с паролями
'''
from flask_sqlalchemy import SQLAlchemy

SQLITE_DB = SQLAlchemy()


'''
    Подключение к базам данных
'''

import logging.config

logging.config.fileConfig(LOG_CONFIG)

MONGODB_CONNECTION = FoodMongoClient(MONGO_HOST, 27017, DATABASE_NAME)
ELASTICSEARCH_CONNECTION = FoodElasticClient(MONGODB_CONNECTION, ELASTICSEARCH_HOST, 9200, "food",
                                             "previews", Logger(logging.getLogger("elastic_search"),
                                                                ALERT_FUNCTION,
                                                                ALERT_SETTINGS))

'''
    Читаем пароли и логины
'''

if not Path('passwords.json').exists():
    Logger(logging.getLogger("test_assistant_api"),
           ALERT_FUNCTION,
           ALERT_SETTINGS).error('Отсутсвует файл с паролями passwords.json')
    exit()

try:
    with open(Path('passwords.json'), 'r', encoding='utf-8') as passf:
        private_data = json.loads(passf.read(), encoding='utf-8')
        PHONE_NUMBER = private_data['phone']
        BILL_PASS = private_data['fns_pass']
        SMTP_MAIL = private_data['smtp_mail']
        SMTP_PASSWORD = private_data['smtp_pass']

except Exception as e:
    Logger(logging.getLogger("test_assistant_api"),
           ALERT_FUNCTION,
           ALERT_SETTINGS).error(f'Ошибка при чтении файла с паролями passwords.json {e}')
    exit()