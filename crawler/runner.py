import argparse
import sys, json
from config import MONGODB_CONNECTION, ELASTICSEARCH_CONNECTION, LOG_PATH, BASE_PATH
from sources.collector import Collector
from datetime import datetime

if __name__ == '__main__':

    # TODO добавить логер (конфиг в logging.ini)

    parser = argparse.ArgumentParser()
    parser.add_argument('--load', action='store_const', const=True)
    parser.add_argument('--save', action='store_const', const=True)
    parser.add_argument('--drop_elastic', action='store_const', const=True)
    parser.add_argument('--migrate', action='store_const', const=True)

    options = parser.parse_args(sys.argv[1:])

    if options.load:
        print(f'Action --load triggered')
        with Collector(base_path=BASE_PATH) as col:
            col.load_all()

    if options.save:
        print('Action --save triggered')
        update_result = MONGODB_CONNECTION.update_mongo()
        with open(LOG_PATH / f'updated_{datetime.now().strftime("%d-%b-%Y_%H:%M:%S.%f")}.json',
                  'w') as saved_report:
            saved_report.write(json.dumps(update_result, indent=4))

    if options.drop_elastic:
        print('Action --drop_elastic triggered')
        ELASTICSEARCH_CONNECTION.delete()

    if options.migrate:
        # TODO uncomment
        # import stanza
        # stanza.download('ru')
        print('Action --migrate triggered')
        ELASTICSEARCH_CONNECTION.migrate()
