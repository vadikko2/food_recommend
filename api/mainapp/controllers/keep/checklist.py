from flask import jsonify, make_response, request
from mainapp.app import db
from mainapp.core.coockies import cookie
from flask import Blueprint
from flask_login import login_required, current_user
import datetime

checklist = Blueprint("checklist", __name__)


@checklist.route("/keep/checklist/<recipe>", methods=["PUT"])
@login_required
def add_checklist(recipe):
    @cookie
    def add(recipe):
        if recipe in db.db["recipes"].distinct("id"):
            new_checklist = {"user": current_user.id, "recipe": recipe}
            new_checklist["checksum"] = db.make_hash(new_checklist)
            new_checklist["done_list"] = []
            new_checklist["@timestamp"] = datetime.datetime.utcnow().timestamp() * 1000
            status = db.add("checklist", new_checklist)
            if status:
                return make_response(jsonify({"message": "Successful adding new checklist."}), 200)
            return make_response(jsonify({"message": "This checklist already exists."}), 200)
        else:
            return make_response(jsonify({"message": f"Recipe id {recipe} not found."}), 404)

    return add(recipe)


@checklist.route("/keep/checklist/<recipe>", methods=["DELETE"])
@login_required
def remove_checklist(recipe):
    @cookie
    def remove(recipe):
        if recipe in db.db["checklist"].find({"user": current_user.id}).distinct("recipe"):
            to_remove_checklist = {"user": current_user.id, "recipe": recipe}
            status = db.remove("checklist", db.make_hash(to_remove_checklist))
            if status:
                return make_response(jsonify({"message": "Successful removing checklist."}), 200)
            return make_response(jsonify({"message": "This checklist does not removed."}), 404)
        else:
            return make_response(jsonify({"message": "This checklist does not exists."}), 404)

    return remove(recipe)
