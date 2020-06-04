from flask import jsonify, make_response
from mainapp.app import db
from mainapp.core.coockies import *
from flask import Blueprint
from flask_login import login_required, current_user
from mainapp.core.recommendations.recommender import Recommend

welcome = Blueprint("welcome", __name__)


@welcome.route("/assistant/welcome", methods=["GET"])
@login_required
def welcome_page():
    @cookie
    def page():
        checklist = db.tojson(db.db["checklist"].find({"user": current_user.id}))
        favorite = db.tojson(db.db["favorite"].find({"user": current_user.id}))
        recipe_ids = list(set([f["recipe"] for f in favorite] + [c["recipe"] for c in checklist]))
        recommend = {"checklist": checklist, "favorite": favorite}
        with Recommend(db) as r:
            recommend['previews'] = r.get_all_previews('recipes', {'id': {'$in': recipe_ids}}, r.preview_fields)
        return make_response(jsonify(recommend), 200)
    return page()