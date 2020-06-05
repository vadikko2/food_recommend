import os
from pathlib import Path

if not Path('api.token').exists():
    print('The token file is not exists.')

API_TOKEN = ''

with open(Path('./api.token'), 'r') as tokenf:
    API_TOKEN = tokenf.read()


SLACK_CHANNEL = '#error-reports'

RABBIT_PORT = 5672
RABBIT_QUEUE_NAME = 'alerts'
RABBIT_LOGIN = 'guest'
RABBIT_PASSWORD = 'guest'

if os.environ.get("DOCKER") == "true":
    RABBIT_HOST = 'rabbitmq'
else:
    RABBIT_HOST = 'localhost'
