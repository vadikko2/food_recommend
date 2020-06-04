import numpy as np
from operator import itemgetter


class Recommend:

    def __init__(self, mongodb_connection):
        self.db = mongodb_connection
        self.preview_fields = {"id": "$id",
                               "name": "$name",
                               "url": "$url",
                               "pict_url": "$pict_url"}
        self.sort_options = {
            "recommendations": 1,
            "most_popular": -1,
            "fastest": -1,
            "biggest": -1,
            "optimal": 1
        }
        self.preview_type_pipelines = {
            "recommendations": [
                {"$project":
                    {
                        "id": 1,
                        "metric":
                            {"$divide": ["$add_in_note",
                                         {"$sum":
                                              ["$like", 1]
                                          }
                                         ]
                             }
                    }
                },
                {"$sort":
                    {
                        "metric": 1,
                        "id": 1
                    }
                },
                {'$skip': None},
                {'$limit': None},
                {'$group':
                    {
                        "_id":
                            {
                                "id": "$id",
                                "metric": "$metric"
                            }
                    }
                }],

            "most_popular": [
                {'$match': {}},
                {'$sort':
                    {
                        "add_in_note": -1,
                        "id": 1
                    }
                },
                {'$skip': None},
                {'$limit': None},
                {'$group':
                    {
                        '_id':
                            {
                                "id": "$id",
                                "metric": "$add_in_note"
                            }
                    }
                }],
            "fastest": [
                {'$match': {}},
                {'$sort':
                    {
                        "time": 1,
                        "id": 1
                    }
                },
                {'$skip': None},
                {'$limit': None},
                {'$group':
                    {
                        '_id':
                            {
                                "id": "$id",
                                "metric": "$time"
                            }
                    }
                }],
            "biggest": [
                {'$match': {}},
                {'$sort':
                    {
                        "portion": -1,
                        "id": 1
                    }
                },
                {'$skip': None},
                {'$limit': None},
                {'$group':
                    {
                        '_id':
                            {
                                "id": "$id",
                                "metric": "$portion"
                            }
                    }
                }],
            "optimal": [
                {"$project":
                    {
                        "id": 1,
                        "metric":
                            {"$divide": ["$time",
                                         {"$sum":
                                              ["$portion", 1]
                                          }
                                         ]
                             }
                    }
                },
                {"$sort":
                    {
                        "metric": 1,
                        "id": 1
                    }
                },
                {'$skip': None},
                {'$limit': None},
                {'$group':
                    {
                        "_id":
                            {
                                "id": "$id",
                                "metric": "$metric"
                            }
                    }
                }]
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.db

    def pipeline(self, view_type, skip=0, limit=10):
        if not view_type in self.preview_type_pipelines:
            raise ValueError('Incorrect view type')
        pipeline = self.preview_type_pipelines[view_type].copy()
        for i, value in enumerate(pipeline):
            if "$skip" in value: pipeline[i] = {"$skip": skip}
            if "$limit" in value: pipeline[i] = {"$limit": limit}
        return pipeline

    def id_finder(self, dict_list):
        return [item['id'] for item in dict_list]

    def get_previews(self, collection, pipeline):
        return self.db.aggregation(collection, pipeline)

    def get_all_previews(self, collection, req, group):
        pipeline = [
            {'$match': req},
            {'$group': {'_id': group}}]
        return self.db.aggregation(collection, pipeline)

    def find_by_condition(self, collection, req={}, skip=0, limit=10):
        return self.db.find(collection, req, skip, limit)

    def find_all_by_condition(self, collection, req):
        return self.db.find_all(collection, req)

    def find_one(self, collection, req={}):
        return self.db.find_one(collection, req)

    def find_similar(self, rk2t, t2rk, kdtree, vectors, favorites, skip=0, limit=10):
        dist, ind = kdtree.query(
            [
                np.mean(
                    [
                        vectors[rk2t[favorite["recipe"]]] for favorite in favorites if favorite["recipe"] in rk2t
                    ], axis=0)
            ], k=100
        )
        keys = list(itemgetter(*ind[0])(t2rk))
        previews = []
        for i, key in enumerate(keys[min(100, skip): min(100, skip + limit)]):
            previews.append(
                {
                    "id": key,
                    "metric": dist[0][i+skip]
                }
            )
        return previews