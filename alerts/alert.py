import pika
import traceback

class Alerts:

    def __init__(self, host, port, login, password, queue_name):
        self.credentials = pika.PlainCredentials(login, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host,
                                                                            port,
                                                                            '/',
                                                                            self.credentials))
        self.queue_name = queue_name
        self.channel = self.connection.channel()
        # Если очередь с указанным именем не существует, queue_declare() создаст ее
        self.channel.queue_declare(queue=self.queue_name)

    def __enter__(self):
        return self

    def alert(self, message):
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()


def alert(message, **kwargs):
    try:
        message = f'{"".join(["-"]*15)}New Message{"".join(["-"]*15)}' \
                  f'\n\n{message}'.encode()
        with Alerts(**kwargs) as alerts_obj:
            alerts_obj.alert(message=message)
    except Exception:
        raise ValueError(f'Error while alert: {traceback.format_exc()}')
