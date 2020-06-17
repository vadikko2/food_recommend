import hashlib
import json
import os
import pickle

from bson.json_util import loads, dumps
from pymongo import MongoClient


class FoodMongoClient:
    def __init__(self, host, port, db):
        self.connection = MongoClient(host, port)
        self.db = self.connection[db]

    def update_mongo(self, path):
        # Проверяем, что папка с файликами есть
        if not path.exists():
            raise ValueError(f"{path} is not exists.")

        updated_ids_dict = {}

        for file in os.listdir(path):
            if not (".json" in file):
                continue
            essence = file.replace(".json", "")
            collection_name = essence

            updated_ids_dict[collection_name] = {'new': [], 'updated': []}
            # забираем чексуммы
            exist_id_set = self.db[collection_name].distinct("id")

            with open(path / file, "r") as ovalfile:
                data = loads(ovalfile.read())

            # Выбираем подгруженные айдишники и чексуммы

            if not data: continue

            for item in data:
                if not item['id'] in exist_id_set:
                    self.easy_add(collection_name, item)
                    updated_ids_dict[collection_name]['new'].append(item['id'])
                else:
                    res = self.db[collection_name].update({'id': item['id']}, item)

                    if res['updatedExisting']:
                        updated_ids_dict[collection_name]['updated'].append(item['id'])

        # Возвращаем список обновленных записей
        return updated_ids_dict

    def get_collections(self):
        return self.db.list_collection_names()

    def aggregation(self, collection, pipeline):
        return self.extract_from_aggregation(self.tojson(self.db[collection].aggregate(pipeline), []))

    def extract_from_aggregation(self, _json):
        if isinstance(_json, dict):
            return _json.get('_id')
        else:
            if _json:
                return list(map(lambda item: item.get('_id'), _json))
            else:
                return _json

    def find(self, collection, req={}, skip=0, limit=10):
        return self.tojson(self.db[collection].find(req).skip(skip).limit(limit))

    def find_all(self, collection, req={}):
        return self.tojson(self.db[collection].find(req))

    def find_one(self, collection, req={}):
        return self.tojson(self.db[collection].find_one(req))

    def name_and_id(self, collection):
        return self.tojson(self.db[collection].aggregate(
            [{"$group": {"_id": {"name": "$name", "id": "$id"}}}, {"$sort": {"_id.id": 1}}]))

    def tojson(self, _bson, garb_fields=['_id', 'checksum']):
        _json = json.loads(dumps(_bson))
        _ = list(map(lambda field: self.del_garb(_json, field), garb_fields)) # TODO test
        # for field in garb_fields:
        #     self.del_garb(_json, field)
        return _json

    def del_garb(self, _json, key):
        if isinstance(_json, dict):
            if key in _json: del _json[key]
        elif isinstance(_json, list):
            for i, item in enumerate(_json):
                if key in _json[i]: del _json[i][key]

    def add(self, collection, document):
        checksums = self.db[collection].distinct("checksum")
        if not document["checksum"] in checksums:
            self.easy_add(collection, document)
            return True
        return False

    def easy_add(self, collection, document):
        self.db[collection].insert(document)

    def remove(self, collection, checksum):
        exists_checksums = self.db[collection].distinct("checksum")
        if checksum in exists_checksums:
            self.db[collection].remove({"checksum": checksum})
            return True
        return False

    def update(self, collection, checksum, field_name, new_value):
        try:
            res = self.db[collection].update({"checksum": checksum}, {"$set": {field_name: new_value}})
            if not res['updatedExisting']:
                return False
            return True
        except:
            return False

    def make_hash(self, o):
        return hashlib.md5(pickle.dumps(o)).hexdigest()
