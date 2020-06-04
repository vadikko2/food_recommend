import json

import requests


# import stanza
# from spacy_stanza import StanzaLanguage


class FoodElasticClient:

    def __init__(self, mongo_client, host, port, index_name, previews_index_name):
        self.url = f"http://{host}:{port}"
        self.index = index_name
        self.previews_index = previews_index_name
        self.mongodb = mongo_client
        # TODO uncomment
        # self.snlp = stanza.Pipeline(lang="ru")
        # self.nlp = StanzaLanguage(self.snlp)

        self.preview_fields = {"id": "$id",
                               "name": "$name",
                               "url": "$url",
                               "pict_url": "$pict_url"}

    def migrate(self):

        '''Собираем рецепты'''

        recipes = self.mongodb.aggregation('recipes', [
            {
                "$group":
                    {
                        "_id":
                            {
                                "id": "$id",
                                "name": "$name",
                                "url": "$url",
                                "pict_url": "$pict_url",
                                "ingredients": "$ingredients.id",
                                "tags": "$tags",
                                "author": "$author.name"
                            }
                    }
            }
        ])
        '''Собираем игредиенты'''
        ingredients = dict(
            [(ingredient['id'], ingredient['name']) for ingredient in self.mongodb.aggregation('ingredients', [
                {
                    "$group":
                        {
                            "_id":
                                {
                                    "id": "$id",
                                    "name": "$name"
                                }
                        }
                }
            ])])
        '''Собираем тэги'''
        tags = dict(
            [(tag['id'], tag['name']) for tag in self.mongodb.aggregation('tags', [
                {
                    "$group":
                        {
                            "_id":
                                {
                                    "id": "$id",
                                    "name": "$name"
                                }
                        }
                }
            ])])
        '''Формируем записи для эластика'''
        previews_list = []
        for i, recipe in enumerate(recipes):

            l_ingredients_set = set()
            l_tags_set = set()
            ingredients_set = set()
            tags_set = set()
            for j, ingredient in enumerate(recipe["ingredients"]):
                # TODO uncomment
                # l_ingredients_set.update(
                #    [word.lemma_ for word in self.nlp(ingredients[recipes[i]["ingredients"][j]].lower())])
                ingredients_set.update(
                    ingredients[recipes[i]["ingredients"][j]].lower().split())
            for j, tag in enumerate(recipe["tags"]):
                # TODO uncomment
                # l_tags_set.update([word.lemma_ for word in self.nlp(tags[recipes[i]["tags"][j]].lower())])
                tags_set.update(tags[recipes[i]["tags"][j]].lower().split())

            recipes[i]["l_ingredients"] = list(l_ingredients_set)
            recipes[i]["l_tags"] = list(l_tags_set)

            recipes[i]["ingredients"] = list(ingredients_set)
            recipes[i]["tags"] = list(tags_set)

            # TODO uncomment
            # recipes[i]["l_name"] = list(set([word.lemma_ for word in self.nlp(recipes[i]["name"].lower())]))

            recipes[i]["s_name"] = list(set(
                recipes[i]["name"].lower().split()))

            # TODO uncomment
            # recipes[i]["l_author"] = list(set(
            #     [word.lemma_ for word in self.nlp(recipes[i]["author"].lower())]))

            recipes[i]["s_author"] = list(set(
                recipes[i]["author"].lower().split()))
        '''Составляем запрос на _bulk'''

        _bulk_data = ""
        for recipe in recipes:
            index_line = json.dumps({"index": {"_index": "food", "_type": "_doc", "_id": recipe["id"], "routing": 0}})
            data_line = json.dumps(recipe)
            _bulk_data += f"{index_line}\n{data_line}\n"

        '''Записываем в elastic'''

        endpoint = f"{self.url}/_bulk"
        resp = requests.post(endpoint, data=_bulk_data,
                             headers={'content-type': 'application/json', 'charset': 'UTF-8'})

        if resp.status_code == 200:
            print(f'Successful _bulk index')
        else:
            print(
                f'Error while _bulk index with code {resp.status_code}: '
                f'{json.dumps(json.loads(resp.content), indent=4)}')

    def delete(self):
        resp = requests.delete(f"{self.url}/{self.index}")
        if resp.status_code == 200:
            print(f'Successful delete index: {json.dumps(json.loads(resp.content), indent=4)}')
        else:
            print(
                f'Error while delete index with code {resp.status_code}: '
                f'{json.dumps(json.loads(resp.content), indent=4)}')

    def find_all(self, skip=0, limit=10):
        query_body = {
            "_source":
                {
                    "includes": list(self.preview_fields.keys())
                }
        }

        response = requests.post(f"{self.url}/_search?from={skip}&size={limit}", data=json.dumps(query_body),
                                 headers={'content-type': 'application/json'})

        if not response.status_code == 200:
            print(
                f"ERROR searching in elasticsearch. Gotten status code {response.status_code}.\n"
                f"Returned data: {json.dumps(json.loads(response.content), indent=4)}")
            return []

        response_body = json.loads(response.content)
        previews = []

        for item in response_body["hits"]["hits"]:
            previews.append({**{"metric": item["_score"]}, **item["_source"]})
        return previews

    def easy_query(self, req_string="", skip=0, limit=10):
        query_body = {
            "query":
                {
                    "dis_max": {
                        "queries": []
                    }
                },
            "_source":
                {
                    "includes": list(self.preview_fields.keys())
                }
        }

        words = req_string.lower().split()  # "".join(self.mystem.lemmatize(req_string.lower())[:-1]).split()
        for filed in ["s_name", "ingredients", "tags", "s_author"]:
            for word in words:
                query_body["query"]["dis_max"]["queries"].append(
                    {
                        "match_phrase_prefix":
                            {
                                filed: word
                            }
                    })

        response = requests.post(f"{self.url}/_search?from={skip}&size={limit}", data=json.dumps(query_body),
                                 headers={'content-type': 'application/json'})

        if not response.status_code == 200:
            print(
                f"ERROR searching in elasticsearch. Gotten status code {response.status_code}.\n"
                f"Returned data: {json.dumps(json.loads(response.content), indent=4)}")
            return []

        response_body = json.loads(response.content)
        previews = []

        for item in response_body["hits"]["hits"]:
            previews.append({**{"metric": item["_score"]}, **item["_source"]})
        return previews

    def intelligence_query(self, req_string, skip=0, limit=10):
        query_body = {
            "query":
                {
                    "dis_max": {
                        "queries": []
                    }
                },
            "_source":
                {
                    "includes": list(self.preview_fields.keys())
                }
        }

        # TODO uncomment
        words = []  # [word.lemma_ for word in self.nlp(req_string.lower())]

        for filed in ["l_name", "l_ingredients", "l_tags", "l_author"]:
            for word in words:
                query_body["query"]["dis_max"]["queries"].append(
                    {
                        "match_phrase_prefix":
                            {
                                filed: word
                            }
                    })

        response = requests.post(f"{self.url}/_search?from={skip}&size={limit}", data=json.dumps(query_body),
                                 headers={'content-type': 'application/json'})

        if not response.status_code == 200:
            print(
                f"ERROR searching in elasticsearch. Gotten status code {response.status_code}.\n"
                f"Returned data: {json.dumps(json.loads(response.content), indent=4)}")
            return []

        response_body = json.loads(response.content)
        previews = []

        for item in response_body["hits"]["hits"]:
            previews.append({**{"metric": item["_score"]}, **item["_source"]})
        return previews
