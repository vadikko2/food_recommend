import concurrent.futures
import logging
import logging.config

from bot.bot import notify
from config import ALERT_FLOWS, LOG_CONFIG

'''
Читаем конфиг для логера
'''

logging.config.fileConfig(LOG_CONFIG)
logger = logging.getLogger("test_assistant_slack_bot")

try:
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ALERT_FLOWS)) as executor:
        executor.map(notify, ALERT_FLOWS)
except Exception as e:
    logger.error(f"Error while notify working: {e}")

