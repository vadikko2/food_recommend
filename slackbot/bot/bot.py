import sys

from slackclient import SlackClient

sys.path.append('../')
from alerts.alert import Alerts
import logging

logger = logging.getLogger("test_assistant_slack_bot")


class Bot:

    def __init__(self, TOKEN, channel):
        self.slack_client = SlackClient(TOKEN)
        self.channel = channel

    def post(self, ch, method, properties, body):
        try:
            self.slack_client.api_call(
                "chat.postMessage",
                channel=self.channel,
                text=body
            )
        except Exception as e:
            logger.error(f"Error while post message from {self.channel}: {e}")

    def __del__(self):
        del self.slack_client


def notify(kwargs):
    try:
        rabbit_channel = Alerts(kwargs['RABBIT_HOST'], kwargs['RABBIT_PORT'], kwargs['RABBIT_PASSWORD'],
                                kwargs['RABBIT_PASSWORD'], kwargs['QUEUE_NAME'])
        bot_client = Bot(kwargs['API_TOKEN'], kwargs['SLACK_CHANNEL'])

        logger.info(f" Bot for {kwargs['SLACK_CHANNEL']} channel getting up.")

        rabbit_channel.channel.basic_consume(queue=kwargs['QUEUE_NAME'],
                                             auto_ack=True,
                                             on_message_callback=bot_client.post)

        logger.info(f" Consumer for {kwargs['QUEUE_NAME']} getting up.")

        rabbit_channel.channel.start_consuming()
    except Exception as e:
        logger.error(f"Some troubles with {kwargs['SLACK_CHANNEL']} bot: {e}")
