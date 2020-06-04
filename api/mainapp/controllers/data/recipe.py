from flask import jsonify, make_response, request
from mainapp.core.recommendations.recipe_recommender import RecipeRecommend
from mainapp.app import cache, db
from mainapp.core.coockies import cookie
from flask import Blueprint
from flask_login import login_required

recipe = Blueprint("recipe", __name__)


@recipe.route("/data/<recipe_id>", methods=["GET"])
@login_required
@cache.cached(query_string=True, timeout=500)
def get_recipe(recipe_id):
    @cookie
    def recipe(recipe_id):
        if not recipe_id: return make_response(jsonify({
            "message": f"Incorrect request params."}), 401)
        with RecipeRecommend(db) as rr:
            resp = rr.find_recipe(recipe_id)
            if not resp: return make_response(jsonify({"message": "Recipe not found."}), 404)

        return make_response(jsonify(resp), 200)
    return recipe(recipe_id)
