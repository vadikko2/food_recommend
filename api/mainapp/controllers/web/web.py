from flask import Blueprint, jsonify, make_response, send_from_directory, render_template, Markup, request
from mainapp.app import cache, db, WEB_PATH

web = Blueprint('web', __name__)

contacts = {"VK": "https://www.vk.com",
            "YouTube": "https://www.youtube.com",
            "Instagram": "https://www.instagram.com",
            "AppStore": "https://www.apple.com/ios/app-store"}


@web.route('/js/<path:path>')
def send_js(path):
    return send_from_directory(WEB_PATH / 'js', path)


@web.route('/css/<path:path>')
def send_css(path):
    return send_from_directory(WEB_PATH / 'css', path)


@web.route('/img/<path:path>')
def send_img(path):
    return send_from_directory(WEB_PATH / 'img', path)


@web.route('/icon-fonts/<path:path>')
def send_icon_fonts(path):
    return send_from_directory(WEB_PATH / 'icon-fonts', path)


@web.route('/')
def index():
    def _index():
        preview_data = list(db.aggregation("recipes", pipeline=[
            {"$sample": {"size": 100}},
            {"$match": {"pict_url": {"$exists": True}}},
            {"$group": {"_id": {"tags": "$tags", "name": "$name", "pict_url": "$pict_url", "url": "$url"}}},
            {"$limit": 5}
        ]))

        cards = [{
            "tags": card["tags"][:min(3, len(card["tags"]))],
            "title": card["name"],
            "summary": Markup(
                "Бла бла бла Описание рецепта, тут надо подумать что вообще писать, потому "
                "что совершенно не понятно.<br/> "
                "Потому что сам рецепт не засунуть."
                "Короче что - то надо придума. <br/> "
                "Вообще здесь это написано чтобы посмотреть как будет выглядеть "
                "текст боьше чем в 1 предложение."
                "Бла бла бла Описание рецепта, тут надо подумать что вообще писать, потому "
                "что совершенно не понятно.<br/> "
                "Потому что сам рецепт не засунуть."
                "Короче что - то надо придума. <br/> "
                "Вообще здесь это написано чтобы посмотреть как будет выглядеть "
                "текст боьше чем в 1 предложение."
                "Бла бла бла Описание рецепта, тут надо подумать что вообще писать, потому "
                "что совершенно не понятно.<br/> "
                "Потому что сам рецепт не засунуть."
                "Короче что - то надо придума. <br/> "
                "Вообще здесь это написано чтобы посмотреть как будет выглядеть "
                "текст боьше чем в 1 предложение."
                "Бла бла бла Описание рецепта, тут надо подумать что вообще писать, потому "
                "что совершенно не понятно.<br/> "
                "Потому что сам рецепт не засунуть."
                "Короче что - то надо придума. <br/> "
                "Вообще здесь это написано чтобы посмотреть как будет выглядеть "
                "текст боьше чем в 1 предложение."

            ),
            "pict_url": card["pict_url"].replace("620x415", "2560x1600"),
            "url": card["url"]}
            for card in preview_data]
        return make_response(render_template("./web/index.html"
                                                 , cards=cards, contacts=contacts))

    return _index()


@web.route("/gallery", methods=["GET"])
def gallery():
    def _gallery():
        page = request.args.get("page", default=1, type=int)
        cards = list(db.aggregation("recipes", pipeline=[
            {"$sort": {"like": -1}},
            {"$match": {"pict_url": {"$exists": True}}},
            {"$group": {
                "_id": {"tags": "$tags", "title": "$name", "pict_url": "$pict_url", "url": "$url", "id": "$id"}}},
            {"$skip": page * 27},
            {"$limit": 27}
        ]))
        for i, _ in enumerate(cards): cards[i]["tags"] = cards[i]["tags"][:min(3, len(cards[i]["tags"]))]
        if page > 1:
            if len(cards) < 27:
                buttons = {"Назад": page - 1}
            else:
                buttons = {"Назад": page - 1, "Дальше": page + 1}
        else:
            buttons = {"Дальше": page + 1}
        return make_response(
            render_template("./web/gallery.html", contacts=contacts, cards=cards,
                            buttons=buttons))

    return _gallery()


@web.route("/recipe/<id>", methods=["GET"])
def recipe(id):
    def _recipe(_id):
        return make_response(
            render_template("./web/blog-single.html", name="Хуйня"))

    return _recipe(id)
