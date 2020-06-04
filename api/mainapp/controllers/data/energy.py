from flask import jsonify, make_response, request
from mainapp.core.recommendations.energy_recommender import EnergyRecommend
from mainapp.app import cache, db
from mainapp.core.coockies import cookie
from flask import Blueprint
from flask_login import login_required

energy = Blueprint("energy", __name__)


@energy.route("/data/energy/<recipe_id>", methods=["GET"])
@login_required
@cache.cached(query_string=True, timeout=500)
def get_energy(recipe_id):
    @cookie
    def energy(recipe_id):
        if not recipe_id: return make_response(jsonify({
            "message": f"Incorrect request params."}), 401)
        with EnergyRecommend(db) as er:
            resp = er.find_energy(recipe_id)
            if not resp: return make_response(jsonify({"message": "Recipe not found."}), 404)
        return make_response(jsonify(resp), 200)
    return energy(recipe_id)
