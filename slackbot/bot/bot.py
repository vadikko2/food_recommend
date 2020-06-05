from slackclient import SlackClient

class Bot:

    def __init__(self, TOKEN, channel):
        self.slack_client = SlackClient(TOKEN)
        self.channel = channel

    def post(self, ch, method, properties, body):
        self.slack_client.api_call(
            "chat.postMessage",
            channel=self.channel,
            text=body
        )

    def __del__(self):
        del self.slack_client
