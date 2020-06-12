import os
from pathlib import Path

if not Path('api.token').exists():
    print('The token file is not exists.'), exit()

API_TOKEN = ''

with open(Path('./api.token'), 'r') as tokenf:
    API_TOKEN = tokenf.read()

RABBIT_LOGIN = 'guest'
RABBIT_PASSWORD = 'guest'

# Before setting ALERT_FLOWS - make sure, that slack channels are exist.
ALERT_FLOWS = [
    dict(QUEUE_NAME='api-errors', SLACK_CHANNEL='#error-reports'),
    dict(QUEUE_NAME='crawler-errors', SLACK_CHANNEL='#crawler-error-reports'),
    dict(QUEUE_NAME='db-updates', SLACK_CHANNEL='#db-updates'),
    dict(QUEUE_NAME='new-users', SLACK_CHANNEL='#new-users'),
]

if os.environ.get("DOCKER") == "true":
    LOG_PATH = Path('./logs')
    LOG_CONFIG = "./logging.ini"
    RABBIT_HOST = 'rabbitmq'
else:
    LOG_PATH = Path("logs/")
    LOG_CONFIG = "logging.ini"
    RABBIT_HOST = 'localhost'

RABBIT_PORT = 5672

ALERT_FLOWS = list(map(lambda flow: {**flow, **dict(API_TOKEN=API_TOKEN,
                                                    RABBIT_HOST=RABBIT_HOST,
                                                    RABBIT_PORT=RABBIT_PORT,
                                                    RABBIT_LOGIN=RABBIT_LOGIN,
                                                    RABBIT_PASSWORD=RABBIT_PASSWORD
                                                    )}, ALERT_FLOWS))
if not LOG_PATH.exists():
    LOG_PATH.mkdir(parents=True)
