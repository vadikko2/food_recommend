from flask import jsonify, make_response, request
from mainapp.app import cache, db, rk2t, t2rk, kdtree, vectors
from flask import Blueprint
from flask_login import login_required, current_user
from mainapp.core.recommendations.recommender import Recommend
from mainapp.core.coockies import cookie

browse = Blueprint("browse", __name__)


@browse.route("/assistant/browse", methods=["GET"])
@cache.cached(query_string=True, timeout=100, key_prefix=f"browse/%s")
def browse_page():
    def page():

        skip = request.args.get("skip", default=0, type=int)
        limit = request.args.get("limit", default=10, type=int)

        if not all([isinstance(skip, int), isinstance(limit, int), not skip < 0, not limit < 0]):
            return make_response(jsonify({
                "message": f"Incorrect [skip] and [limit] request params"}), 401)

        try:
            with Recommend(db) as r:
                try:
                    favorites = r.get_previews('favorite', pipeline=[
                        {"$match": {"user": current_user.id}},
                        {"$group": {"_id": {"recipe": "$recipe"}}}
                    ])
                except:
                    favorites = []

                if False:  # en(favorites): TODO раскомментировать. тут будут отдаваться рекоммендации от нашего алгоритма
                    recommendations = r.find_similar(rk2t, t2rk, kdtree, vectors, favorites, skip, limit)
                else:
                    recommendations = r.get_previews("recipes",
                                                     pipeline=r.pipeline('recommendations', skip, limit))
                tops_dict = {
                    "recommendations": recommendations,
                    "most_popular": r.get_previews("recipes",
                                                   pipeline=r.pipeline('most_popular', skip, limit)),
                    "fastest": r.get_previews("recipes", pipeline=r.pipeline('fastest', skip, limit)),
                    "biggest": r.get_previews("recipes", pipeline=r.pipeline('biggest', skip, limit)),
                    "optimal": r.get_previews("recipes", pipeline=r.pipeline('optimal', skip, limit)),
                }
                tops = {}
                for top_type, resp in tops_dict.items():
                    previews = r.get_all_previews(collection='recipes',
                                                  req={
                                                      'id':
                                                          {
                                                              '$in': r.id_finder(resp)
                                                          }
                                                  },
                                                  group=r.preview_fields)
                    for i, preview in enumerate(previews):
                        for item in resp:
                            if item["id"] == preview["id"]: previews[i]["metric"] = item["metric"]
                    tops[top_type] = {"previews": previews, "sort_option": r.sort_options[top_type]}

                return make_response(jsonify(tops), 200)
        except Exception as e:
            return make_response(jsonify({"message": f"Oops, something happen wrong: {e}"}), 500)

    return page()


@browse.route("/assistant/browse/paginator/<view_type>", methods=["GET"])
@cache.cached(query_string=True, timeout=100, key_prefix=f"browse/%s")
def browse_paginator(view_type):
    def paginator(view_type):
        skip = request.args.get("skip", default=0, type=int)
        limit = request.args.get("limit", default=10, type=int)

        if not all([isinstance(skip, int), isinstance(limit, int), not skip < 0, not limit < 0]):
            return make_response(jsonify({
                "message": f"Incorrect [skip] and [limit] request params"}), 401)

        try:
            with Recommend(db) as r:
                if not view_type in r.preview_type_pipelines:
                    raise ValueError(
                        f"View type error. U have to use one of following endpoints: "
                        f"{tuple(r.preview_type_pipelines.keys())}")
                resp = r.get_previews("recipes", pipeline=r.pipeline(view_type, skip, limit))
                previews = r.get_all_previews(collection='recipes',
                                              req={
                                                  'id':
                                                      {
                                                          '$in': r.id_finder(resp)
                                                      }
                                              },
                                              group=r.preview_fields)
                for i, preview in enumerate(previews):
                    for item in resp:
                        if item["id"] == preview["id"]: previews[i]["metric"] = item["metric"]
                previews = {"previews": previews, "sort_option": r.sort_options[view_type]}
                return make_response(jsonify(previews), 200)
        except Exception as e:
            return make_response(jsonify({"message": f"Oops, something happen wrong: {e}"}), 500)

    return paginator(view_type)
