import traceback
import sys
from alert import alert
sys.path.append('../')
from api.config import ALERT_SETTINGS
message = 'Empty message'
try:
    1 / 0
except Exception as e:
    message = traceback.format_exc()

alert(message, **ALERT_SETTINGS)
