import requests
from lxml import html
import re
import json


class EdaRu:
    __name__ = 'edaru'

    def __init__(self, base_path):

        db_name = 'recipes.json'
        ingredients_name = 'ingredients.json',
        tags_name = 'tags.json'
        database_path = base_path / self.__name__

        self.db_name = database_path / db_name
        self.ingredients_name = database_path / ingredients_name
        self.tags_name = database_path / tags_name

        self.db = []
        self.ingredients_db = {}
        self.tags_db = {}

    def get_recipes(self, page=1):
        url = 'https://eda.ru/recepty?page={}'

        return url.format(page)

    def get_search_url(self, query: str, page=1):
        url = 'https://eda.ru/recipesearch?q={}&onlyEdaChecked=true&page={}'  # page не работает - сук тупая
        return url.format(query.replace(' ', '+'), page)

    def get_tree(self, search_url: str):

        response = requests.get(search_url)

        if response.status_code == 200:

            body = response.text

            return html.fromstring(body)

        elif response.status_code == 404:
            print('Not Found. URL: {}'.format(search_url))

            return False

    def pars_ingredients(self, item):

        ingredients = item.xpath(
            './/p[@class="ingredients-list__content-item content-item js-cart-ingredients"]/@data-ingredient-object')
        ingredients = [json.loads(x) for x in ingredients]

        for ingredient in ingredients:
            self.ingredients_db.update({ingredient['id']: ingredient['name']})
            del ingredient['name']

        return ingredients

    def convert_nutrision_item(self, nutrition_item):

        name = nutrition_item.xpath('.//p[@class = "nutrition__name"]/text()')
        weight = nutrition_item.xpath('.//p[@class = "nutrition__weight"]/text()')
        percent = nutrition_item.xpath('.//p[@class = "nutrition__percent"]/text()')

        return {'name': ' '.join(name),
                'weight': ' '.join(weight),
                'percent': ' '.join(percent)}

    def get_food_energy_and_comments(self, recipes_url: str):

        tree = self.get_tree(recipes_url)

        if tree:
            nutrition_list = [x for x in tree.xpath('//ul[@class="nutrition__list"]/li')]

            for i, item in enumerate(nutrition_list):
                nutrition_list[i] = self.convert_nutrision_item(item)

            comments = ''.join(
                tree.xpath('//div[@class="comments print-invisible js-comments js-social-widget-trigger"]/p/text()'))

            comments = int(re.sub(r'[^0-9]', '', comments))

            pict_url = self.get_pict_url(tree)

            return nutrition_list, comments, pict_url

        return [], 0

    def convert_to_min(self, time_str):

        hour = 0
        _min = 0
        if 'час' in time_str:
            hour, time_str = time_str.split('час')
            hour = int(re.sub(r'[^0-9]', '', hour))

        if 'мин' in time_str:
            _min = int(re.sub(r'[^0-9]', '', time_str))

        return hour * 60 + _min

    def get_time_portion_info(self, item):

        portion = re.sub(r'[^0-9]', '', ''.join(item.xpath('.//span[@class="portions-counter"]/span/text()')))
        time = ''.join(item.xpath('.//span[@class="prep-time"]/text()'))

        return int(portion), self.convert_to_min(time)

    def get_social_info(self, item):

        add_in_note = ''.join(
            item.xpath('.//span[@class="widget-list__favorite-count tooltip js-tooltip"]/span/text()'))
        like = ''.join(item.xpath('.//span[@class="widget-list__like-count"]/span/text()'))
        dis = ''.join(
            item.xpath('.//span[@class="widget-list__like-count widget-list__like-count_dislike"]/span/text()'))

        return int(like), int(dis), int(add_in_note)

    def get_author_info(self, item):

        name = ', '.join(item.xpath('.//span[@class="horizontal-tile__author-link js-click-link"]/text()'))
        url = ', '.join(item.xpath('.//span[@class="horizontal-tile__author-link js-click-link"]/@data-href'))

        return {'name': name, 'url': url}

    def get_tags(self, item):

        tags = item.xpath('.//ul[@class="breadcrumbs"]/li/a')

        for i, tag in enumerate(tags):
            name = ''.join(tag.xpath('.//span/text()'))
            url = ''.join(tag.xpath('.//@href'))

            if not name in self.tags_db:
                self.tags_db.update({name: [url, url.split('/')[-1]]})

            tags[i] = self.tags_db[name][1]

        return tags

    def get_pict_url(self, item):

        url = item.xpath('.//div[@class="recipe__print-cover"]/img/@src')

        return ''.join(url)

    def pars_item(self, item):

        name = re.sub(r'[\n]', '', ''.join(
            item.xpath('.//h3[@class="horizontal-tile__item-title item-title"]/a/span/text()'))).strip()
        url = 'https://eda.ru' + ''.join(
            [x for x in item.xpath('.//h3[@class="horizontal-tile__item-title item-title"]/a/@href') if
             not re.findall('https', x)])

        ingredients = self.pars_ingredients(item.xpath('.//div[@class="ingredients-list__content"]')[0])

        author = self.get_author_info(item)
        tags = self.get_tags(item)

        portion, time = self.get_time_portion_info(item)

        like, dis, add_in_note = self.get_social_info(item)

        food_energy, comments, pict_url = self.get_food_energy_and_comments(url)

        return (name, url, ingredients, author,
                food_energy, tags,
                portion, time, like,
                dis, add_in_note,
                comments, pict_url)

    def get_items(self, search_url: str):

        tree = self.get_tree(search_url)

        if tree:
            return tree.xpath(
                '//div[@class="tile-list__horizontal-tile horizontal-tile js-portions-count-parent js-bookmark__obj"]')

        return []

    def get_page(self, search_url: str):

        items = self.get_items(search_url)

        if items:
            for item in items:
                item_json = {'id': '',
                             'url': '',
                             'ingredients': {},
                             'author': {},
                             'food_energy': [],
                             'portion': 0,
                             'time': 0,
                             'like': 0,
                             'dis': 0,
                             'pict_url': '',
                             'add_in_note': 0,
                             'comments': 0,
                             'tags': [],
                             'checksum': ''}

                (name, url, ingredients,
                 author, food_energy, tags,
                 portion, time, like, dis,
                 add_in_note, comments, pict_url) = self.pars_item(item)

                item_json['id'] = url.split('/')[-1].split('-')[-1]
                item_json['name'] = name
                item_json['url'] = url
                item_json['portion'] = portion
                item_json['time'] = time
                item_json['like'] = like
                item_json['dis'] = dis
                item_json['add_in_note'] = add_in_note
                item_json['comments'] = comments
                item_json['pict_url'] = pict_url
                item_json['ingredients'] = ingredients
                item_json['author'] = author
                item_json['tags'] = tags
                item_json['food_energy'] = food_energy

                item_json['checksum'] = hash(json.dumps(item_json))

                self.db.append(item_json)

            return True

        return False

    def add_checksum(self, db):
        for item in db:
            item.update({'checksum': hash(json.dumps(item))})
        return db

    def convert_ingredients_db(self):
        db = [{'id': str(key), 'name': value} for key, value in self.ingredients_db.items()]
        return self.add_checksum(db)

    def convert_tags_db(self):
        db = [{'id': str(value[1]), 'name': key, 'url': value[0]} for key, value in self.tags_db.items()]
        return self.add_checksum(db)

    def dump_json(self, _json, name):
        print('Saving ' + str(name))

        with open(name, 'wt') as f:
            json.dump(_json, f, sort_keys=False, indent=4, ensure_ascii=False)

    def load(self, max_page=None):

        page = 1
        while True:

            print("Loading page {}".format(page))
            search_url = self.get_recipes(page)

            parsed_page = self.get_page(search_url)

            if not parsed_page:
                break

            if (not max_page is None) & (page >= max_page):
                break

            page += 1

        self.dump_json(self.db, self.db_name)
        self.dump_json(self.convert_ingredients_db(), self.ingredients_name)
        self.dump_json(self.convert_tags_db(), self.tags_name)

