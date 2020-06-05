import sys

from bot.bot import Bot
from config import RABBIT_QUEUE_NAME, RABBIT_PORT, RABBIT_HOST, RABBIT_PASSWORD, API_TOKEN, SLACK_CHANNEL

sys.path.append('../')
from alerts.alert import Alerts

rabbit_channel = Alerts(RABBIT_HOST, RABBIT_PORT, RABBIT_PASSWORD, RABBIT_PASSWORD, RABBIT_QUEUE_NAME)
bot_client = Bot(API_TOKEN, SLACK_CHANNEL)
rabbit_channel.channel.basic_consume(queue=RABBIT_QUEUE_NAME,
                                     auto_ack=True,
                                     on_message_callback=bot_client.post)

print(' [*] Waiting for messages. To exit press CTRL+C')
rabbit_channel.channel.start_consuming()
