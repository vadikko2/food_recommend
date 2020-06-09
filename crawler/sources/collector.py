from config import ALERT_FUNCTION, ALERT_SETTINGS
from config import LOG_CONFIG, Logger

import logging.config

logging.config.fileConfig(LOG_CONFIG)
collector_logger = Logger(logging.getLogger("test_assistant_crawler.collector"),
                          ALERT_FUNCTION,
                          ALERT_SETTINGS)


class Collector:

    def __init__(self, base_path, sources):
        self.sources = list(
            map(lambda source: sources[source](base_path,
                                               Logger(logging.getLogger(f"test_assistant_crawler.{source}"),
                                                      ALERT_FUNCTION,
                                                      ALERT_SETTINGS)),
                sources))

    def load_all(self):

        for module in self.sources:
            collector_logger.info(f'Выполняется загрузка данных из источника {module.__name__}', alert=True)
            module.load()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i, source in enumerate(self.sources): del self.sources[i]
