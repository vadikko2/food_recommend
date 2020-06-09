import argparse
import logging.config
import sys

from config import ELASTICSEARCH_CONNECTION, BASE_PATH, DATA_SOURCES, ALERT_FUNCTION, \
    ALERT_SETTINGS, DB_INFO_ALERT_SETTINGS
from config import LOG_CONFIG, Logger
from sources.collector import Collector

logging.config.fileConfig(LOG_CONFIG)
logger = Logger(logging.getLogger("test_assistant_crawler.runner"),
                ALERT_FUNCTION,
                ALERT_SETTINGS)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--load', action='store_const', const=True)
    parser.add_argument('--save', action='store_const', const=True)
    parser.add_argument('--drop_elastic', action='store_const', const=True)
    parser.add_argument('--migrate', action='store_const', const=True)

    options = parser.parse_args(sys.argv[1:])

    col = Collector(base_path=BASE_PATH, sources=DATA_SOURCES)

    if options.load:
        logger.info('Action --load triggered', alert=True)
        ALERT_FUNCTION('Action --load triggered', **DB_INFO_ALERT_SETTINGS)

        col.load_all()  # TODO добавить какой-нибудь report об окончании загрузки с информацией о результатах

    if options.save:
        logger.info('Action --save triggered', alert=True)
        ALERT_FUNCTION('Action --save triggered', **DB_INFO_ALERT_SETTINGS)

        report = col.save_all()

        ALERT_FUNCTION(report, **DB_INFO_ALERT_SETTINGS)

        logger.info('Action --save completed', alert=True)

        ALERT_FUNCTION('Action --save completed', **DB_INFO_ALERT_SETTINGS)

    if options.drop_elastic:
        logger.info('Action --drop_elastic triggered', alert=True)
        ALERT_FUNCTION('Action --drop_elastic triggered', **DB_INFO_ALERT_SETTINGS)

        ELASTICSEARCH_CONNECTION.delete()

    if options.migrate:
        import stanza

        stanza.download('ru')

        logger.info('Action --migrate triggered', alert=True)
        ALERT_FUNCTION('Action --migrate triggered', **DB_INFO_ALERT_SETTINGS)

        ELASTICSEARCH_CONNECTION.migrate()
