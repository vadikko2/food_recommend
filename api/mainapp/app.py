import json

import requests
from flask import Flask, make_response, jsonify
from flask_caching import Cache
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_mail import Mail

'''
    Импорт модуля для работы с моделями
'''

from config import *
from models import models

'''
    Читаем конфиг для логера
'''

logging.config.fileConfig(LOG_CONFIG)
logger = Logger(logging.getLogger("test_assistant_api"),
                ALERT_FUNCTION,
                ALERT_SETTINGS)

new_users_logger = Logger(logging.getLogger("test_assistant_api"),
                          ALERT_FUNCTION,
                          NEW_USERS_ALERT_SETTINGS)

'''
    Подключаемся к базам данных
'''

try:
    db = MONGODB_CONNECTION
    sqlite_db = SQLITE_DB
    elastic = ELASTICSEARCH_CONNECTION
except Exception as e:
    message = f'Ошибка подключения к базам данных: {e}'
    logger.error(message)
    exit()

'''
    Выгрузка векторов для рекоммендаций
'''

try:
    rn2t, rk2t, t2rn, t2rk = models.get_w2v_kdtree_dicts(MODELS_PATH)
    kdtree = models.get_w2v_kdtree(MODELS_PATH)
    vectors = models.get_vectors(MODELS_PATH)
except Exception as e:
    message = f'Ошибка чтения моделей файла с моделями: {e}'
    logger.error(message)
    exit()

'''
    Подключение к модулю, предоставлющему инфу по чекам
'''

response = requests.get('https://proverkacheka.nalog.ru:9999/v1/mobile/users/login',
                        auth=(PHONE_NUMBER, BILL_PASS))

if not response.status_code == 200:
    message = f'Ошибка авторизации в сервисе предоставления информации по чекам: {response.content.decode()}'
    logger.error(message)

else:
    logger.info(
        f'Успешная авторизация на proverkacheka.nalog.ru \n'
        f'Ответ сервера: CODE {response.status_code} {json.dumps(json.loads(response.content.decode()), indent=4)}')

'''
    Подключение к Redis
'''

try:
    cache = Cache(config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': f'redis://{REDIS_HOST}:{REDIS_PORT}/0'})
except Exception as e:
    message = f'Ошибка при подключении к Redis: {e}'
    logger.error(message)
    exit()

'''
    Запуск API
'''
try:
    app = Flask(__name__)

    app.config["SECRET_KEY"] = "9OLWxND4o83j4K4iuopO"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
    app.config["JSON_SORT_KEYS"] = False

    SQLITE_DB.init_app(app)
    cache.init_app(app)
    mail = Mail()

    app.config.update(dict(
        MAIL_SERVER="smtp.gmail.com",
        MAIL_PORT=587,
        MAIL_USE_TLS=True,
        MAIL_USERNAME=SMTP_MAIL,
        MAIL_PASSWORD=SMTP_PASSWORD,
    ))

    mail.init_app(app)
    jwt = JWTManager(app)

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from mainapp.core.users.models import *


    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))


    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return make_response(jsonify({"message": "Please login or signup"}), 400)


    with app.app_context():
        from mainapp.controllers.web.web import web

        app.register_blueprint(web)

        from mainapp.controllers.assistant.welcome import welcome

        app.register_blueprint(welcome)

        from mainapp.controllers.assistant.browse import browse

        app.register_blueprint(browse)

        from mainapp.controllers.data.recipe import recipe

        app.register_blueprint(recipe)

        from mainapp.controllers.data.energy import energy

        app.register_blueprint(energy)

        from mainapp.controllers.authentication.auth import auth

        app.register_blueprint(auth)

        from mainapp.controllers.authentication.main import main

        app.register_blueprint(main)

        from mainapp.controllers.keep.favorite import favorite

        app.register_blueprint(favorite)

        from mainapp.controllers.keep.checklist import checklist

        app.register_blueprint(checklist)

        from mainapp.controllers.keep.update import update

        app.register_blueprint(update)

        from mainapp.controllers.bills.bills import bills

        app.register_blueprint(bills)

        from mainapp.controllers.search.search import search

        app.register_blueprint(search)

    SQLITE_DB.create_all(app=app)
except Exception as e:
    message = f'Ошибка при страте API: {e}'
    logger.error(message)
    exit()
