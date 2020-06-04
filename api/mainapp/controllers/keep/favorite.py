from flask import jsonify, make_response, request
from mainapp.app import db
from mainapp.core.coockies import cookie
from flask import Blueprint
from flask_login import login_required, current_user
import datetime

favorite = Blueprint("favorite", __name__)


@favorite.route("/keep/favorite/<recipe>", methods=["PUT"])
@login_required
def add_favorite(recipe):
    @cookie
    def add(recipe):
        if recipe in db.db["recipes"].distinct("id"):
            new_favorite = {"user": current_user.id, "recipe": recipe}
            new_favorite["checksum"] = db.make_hash(new_favorite)
            new_favorite["@timestamp"] = datetime.datetime.utcnow().timestamp() * 1000
            status = db.add("favorite", new_favorite)
            if status:
                return make_response(jsonify({"message": "Successful adding new favorite."}), 200)
            return make_response(jsonify({"message": "This favorite already exists."}), 200)
        else:
            return make_response(jsonify({"message": f"Recipe id {recipe} not found."}), 404)

    return add(recipe)


@favorite.route("/keep/favorite/<recipe>", methods=["DELETE"])
@login_required
def remove_favorite(recipe):
    @cookie
    def remove(recipe):
        if recipe in db.db["favorite"].find({"user": current_user.id}).distinct("recipe"):
            to_remove_favorite = {"user": current_user.id, "recipe": recipe}
            status = db.remove("favorite", db.make_hash(to_remove_favorite))
            if status:
                return make_response(jsonify({"message": "Successful removing favorite."}), 200)
            return make_response(jsonify({"message": "This favorite does not removed."}), 404)
        else:
            return make_response(jsonify({"message": "This favorite does not exists."}), 404)

    return remove(recipe)
