import logging
from collections import OrderedDict
from flask import request
from .. import handler


def syslog(**kwargs):
    try:
        remote_addr = request.remote_addr if request.environ.get('HTTP_X_FORWARD_FOR') is None else request.environ.get(
            'HTTP_X_FORWARD_FOR')

        params = OrderedDict({
            "EventID": kwargs.get("EventID", "1"),
            "EventName": kwargs.get("ServerAddress", request.url),
            "ServerHostName": kwargs.get("ServerHostName", request.host),
            "ClientAddress": kwargs.get("TargetAddress", remote_addr),
            "ClientHostName": kwargs.get("TargetHostName", remote_addr),
            "Result": kwargs.get("Result", "200"),
            "Detail": kwargs.get("")
        })

        logger = logging.getLogger('syslog')
        logger.addHandler(handler)
        logger.info(';'.join(f"{k}=\"{v}\"" for k, v in params.items()))
    except Exception as e:
        print('Logging exception:', e)
