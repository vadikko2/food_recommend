import hashlib
import json
import pprint
import re

import requests
from lxml import html
from lxml.etree import tostring
from tqdm import tqdm


class EdimDoma:
    __name__ = 'edimdoma'

    def __init__(self, base_path, logger):
        self.logger = logger

        self.url = "https://www.edimdoma.ru/retsepty?page=#"
        self.database_path = base_path

        if not self.database_path.exists(): self.database_path.mkdir(parents=True)

        self.recipe_urls = set()

        self.recipes = []
        self.tags = []
        self.ingredients = []

    def load(self):
        number_of_pages = 0

        '''
        Получаем число страниц с рецептами
        '''

        page = requests.get("https://www.edimdoma.ru/retsepty").content
        tree = html.fromstring(page)
        try:
            pages = tree.xpath('/html/body/div[6]/div[3]/div/div[1]/div[4]/div[2]/div')[0]
        except Exception as e:
            message = f'Ошибка при попытке выбора списка номеров сьтраниц с рецептами: {e}'
            self.logger.error(message, alert=True)
            return None

        for item in pages:
            try:
                number_of_pages = max(number_of_pages, int(item.text))
            except:
                pass

        '''
        Идем по всем страницам и парсим ссылки на рецепты
        '''
        for page in tqdm(range(1, 2), desc='Загрузка списка рецептов'):  # TODO заменить на number_of_pages
            try:
                self.parse_page(page)
            except Exception as e:
                message = f'Ошибка при обработке страницы:\n {e}'
                self.logger.error(message, alert=True)

        '''
        Загружаем сами рецепты
        '''
        for url in tqdm(self.recipe_urls, desc='Загрузка описаний рецептов'):
            try:
                self.parse_recipes(url)
            except Exception as e:
                message = f'Ошибка при парсинге страницы с рецептом:\n {e}'
                self.logger.error(message, alert=True)

    def parse_page(self, number):
        page_url = self.url.replace('#', str(number))

        try:
            page = requests.get(page_url).content.decode()
        except Exception as e:
            raise ValueError(f'Ошибка загрузки страницы {page_url}: {e}')

        try:
            self.recipe_urls.update(list(
                map(lambda x: x.replace('href="', '').replace('"', '').replace('#comments_anchor', ''),
                    re.findall(r'href="/retsepty/\d+-\S+"', page))))
        except Exception as e:
            raise ValueError(f'Ошибка при поиске ссылки на рецепт по шаблону: {e}')

    def parse_recipes(self, url):
        recipe_url = self.url.replace('/retsepty?page=#', url)

        try:
            recipe_page = requests.get(recipe_url).content.decode()
        except Exception as e:
            raise ValueError(f'Ошибка при загрузке страницы с рецптом {recipe_url}: {e}')

        try:

            _id = re.findall(r'/(\d+)-', url)[0]

            # Название рецепта
            name = re.findall(r'<h1 class="recipe-header__name">(.*?)<', recipe_page)[0]

            # Ссылка на картинку
            pict_url = re.findall(r'"https://e0.edimdoma.ru/data/recipes/.*?"', recipe_page)[0].replace('"', '')

            # Колисество лайков
            like = int(re.findall(
                r'<div class="button button_like-it ajax_like_block button_pink show_popup_auth ">'
                r'<span class="fonticon fonticon_like ajax_like_data" '
                r'data-add-class="button_red" data-object-id="\d+" '
                r'data-object-type="recipe" data-remove-class="button_pink"></span>'
                r'<span class="ajax_like_btn_text">(\d+)</span></div>'
                , recipe_page)[0]) or 0

            # Количество сохранений в закладки
            add_in_note = int(re.findall(
                r'<div class="button button_rate button_transparent">'
                r'<span class="fonticon fonticon_rate-button">'
                r'</span><span>(\d+)</span></div>',
                recipe_page)[0]) or 0

            # Колисество коментариев
            comments = int(re.findall(
                r'<div class="button button_comments button_transparent">'
                r'<span class="fonticon fonticon_comments-button"></span>'
                r'<span>(\d+)</span>'
                r'</div>', recipe_page)[0]) or 0

            # Число порций
            portion = int(re.findall(
                r'<input type="text" name="servings" id="servings" value="(\d+)" min="1" class="field__input" />',
                recipe_page)[0]) or \
                      int(re.findall(
                          r'<input type="text" name="servings" id="servings" value="4" min="1" class="field__input">',
                          recipe_page)[0])

            # Ингредиенты
            ingredients_with_amounts = list(self.parse_ingredients(recipe_page))
            rec_ing = list(map(lambda ing: {'id': ing[0]['id'], 'amount': ing[1]}, ingredients_with_amounts))
            self.ingredients += list(map(lambda ing: self.add_checksum([ing[0]])[0], ingredients_with_amounts))

        except Exception as e:
            raise ValueError(f'Ошибка при извлечении описаний рецепта {recipe_url} по шаблонам: {e}')

        recipe = {
            "id": f'{self.__name__}:{_id}',
            "url": recipe_url,
            "name": name,
            "pict_url": pict_url,
            "like": like,
            "add_in_note": add_in_note,
            "comments": comments,
            "portion": portion,
            "ingredients": rec_ing
        }

        pprint.pprint(recipe)

    def parse_ingredients(self, page):
        tree = html.fromstring(page)
        ingredients_slice = tostring(tree.xpath('//*[@id="recipe_ingredients_block"]')[0], encoding='utf-8').decode()
        rows = re.findall(r'<tr class="definition-list-table__tr">(.*?)</tr>', ingredients_slice)
        for row in rows:  # TODO Добавить поддержку вот таких рецептов https://www.edimdoma.ru/retsepty/139209-vengerskaya-vatrushka-turos-taska
            name = re.findall(r'<span class="recipe_ingredient_title">(.*?)</span>', row)[0]
            ingredient_id = hashlib.md5(name.encode()).hexdigest()
            amount = 1
            yield {'name': name, 'id': ingredient_id}, amount

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.recipes
        del self.ingredients
        del self.tags
        del self.recipes

    def add_checksum(self, db):
        for item in db:
            item.update({'checksum': hash(json.dumps(item))})
        return db
