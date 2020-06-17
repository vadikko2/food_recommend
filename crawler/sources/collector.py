import json
import logging.config
from datetime import datetime
from traceback import format_exc as trace

from config import ALERT_FUNCTION, ALERT_SETTINGS, DB_INFO_ALERT_SETTINGS, MONGODB_CONNECTION, LOG_PATH
from config import LOG_CONFIG, Logger

logging.config.fileConfig(LOG_CONFIG)
errors_logger = Logger(
    logging.getLogger("test_assistant_crawler.collector"),
    ALERT_FUNCTION,
    ALERT_SETTINGS
)

db_update_logger = Logger(
    logging.getLogger("test_assistant_crawler.db_updater"),
    ALERT_FUNCTION,
    DB_INFO_ALERT_SETTINGS
)


class Collector:

    def __init__(self, base_path, sources):
        self.sources = list(
            map(lambda source: sources[source](base_path / source,
                                               Logger(logging.getLogger(f"test_assistant_crawler.{source}"),
                                                      ALERT_FUNCTION,
                                                      ALERT_SETTINGS)),
                sources))

    def load_all(self):

        for module in self.sources:
            db_update_logger.info(f'Выполняется загрузка данных из источника {module.__name__}', alert=True)
            module.load()

    def save_all(self):
        save_report = {}
        for module in self.sources:
            db_update_logger.info(f'Выполняется сохранение данных для источника {module.__name__}', alert=True)

            try:
                update_result = MONGODB_CONNECTION.update_mongo(module.database_path)
            except ValueError:
                errors_logger.error(f'Ошибка при обновлении базы данными от источника {module.__name__}: {trace}')
                errors_logger.warning(f'Этап сохранения данных из источника {module.__name__} будет пропущен',
                                      alert=True)
                continue

            with open(LOG_PATH / f'{module.__name__}_updated_{datetime.now().strftime("%d-%b-%Y_%H:%M:%S.%f")}.json',
                      'w') as reportf:
                report = json.dumps(update_result, indent=4, ensure_ascii=False)
                reportf.write(report)

            save_report[module.__name__] = {}
            for collection in update_result:
                save_report[module.__name__][collection] = {}
                for _type in update_result[collection]:
                    save_report[module.__name__][collection][_type] = len(update_result[collection][_type])

        return json.dumps(save_report, indent=4, sort_keys=True, ensure_ascii=False)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for i, source in enumerate(self.sources): del self.sources[i]
