from flask import jsonify, make_response, request
from mainapp.app import cache, elastic
from flask import Blueprint
from flask_login import login_required
from mainapp.core.coockies import cookie
import traceback
search = Blueprint("search", __name__)


@search.route("/search", methods=["GET"])
@login_required
@cache.cached(timeout=500, query_string=True)
def get_search():
    @cookie
    def search():
        sort_type = bool(request.args.get("type", default=0, type=int))
        query_string = request.args.get("q", default="", type=str)
        skip = request.args.get("skip", default=0, type=int)
        limit = request.args.get("limit", default=10, type=int)

        try:
            if not query_string:
                previews = elastic.find_all(skip, limit)
            else:
                if not sort_type:
                    previews = elastic.easy_query(query_string, skip, limit)
                else:
                    # TODO uncomment
                    previews = []#elastic.intelligence_query(query_string, skip, limit)
            previews = {"previews": previews, "sort_option": 1}
            return make_response(jsonify(previews), 200)
        except Exception as e:
            traceback.print_exc()
            return make_response(jsonify({"message": f"Oops, something happen wrong: {e}"}), 500)
    return search()


@search.route("/preview", methods=["GET"])
@login_required
@cache.cached(timeout=500, query_string=True)
def get_preview():
    @cookie
    def preview():
        pass

    return preview()