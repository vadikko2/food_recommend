from flask import request, jsonify, make_response
from mainapp.app import db
from mainapp.core.coockies import cookie
from flask import Blueprint
from flask_login import login_required, current_user

update = Blueprint("update", __name__)


@update.route("/keep/update", methods=["POST"])
@login_required
def update_item():
    @cookie
    def update():
        r = request.get_json(force=True)

        try:
            if not len(list(r.keys())) == 2:
                raise ValueError(f"Incorrect number of request json params: expected 2, gotten {len(list(r.keys()))}")
            if (not "recipe" in r) or (not "done_list" in r):
                raise ValueError(
                    f"Incorrect request json params: expected [recipe, done_list], gotten {list(r.keys())}")
            if (not isinstance(r['recipe'], str)) or (not isinstance(r["done_list"], list)) or (
                    not all([isinstance(item, int) for item in r["done_list"]])):
                raise ValueError(f"Incorrect type of request json params: expected recipe: str, done_list: list(int)")
        except Exception as e:
            return make_response(jsonify({
                "message": f"Incorrect request parameters set: {e})"}), 401)

        try:
            checksum = db.make_hash({"user": current_user.id, "recipe": r["recipe"]})
            checklist_check = db.update("checklist", checksum, "done_list", r["done_list"])
            if not checklist_check:
                return make_response(jsonify(
                    {"message": "Update error."}))
            return make_response(jsonify({"message": "Success"}), 200)
        except Exception as e:
            make_response(jsonify({"message": f"Incorrect request json format: {e}"}), 400)

    return update()
