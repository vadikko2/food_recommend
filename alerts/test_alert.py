import traceback
from alert import Alerts


with Alerts(host='localhost', port=5672, login='guest', password='guest', queue_name='api-errors') as alert_obj:
    message = 'Empty message'
    try:
        1 / 0
    except Exception as e:
        message = traceback.format_exc()

    alert_obj.alert(message)
