import pika


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

    def alert(self, message):
        self.channel.basic_publish(exchange='', routing_key=self.queue_name, body=message)

    def catch_alert(self):
        method_frame, header_frame, body = self.channel.basic_get('alerts')
        message = None
        if method_frame:
            message = body.decode()
            self.channel.basic_ack(method_frame.delivery_tag)
        return message

    def __del__(self):
        self.connection.close()
