from flask import Blueprint, jsonify, make_response
from flask_login import current_user
from flask_login import login_required
from mainapp.app import cache
from mainapp.core.coockies import cookie
main = Blueprint('main', __name__)


@main.route('/profile', methods=['GET'])
@login_required
@cache.cached(query_string=True, timeout=100)
def profile():
    @cookie
    def _profile():
        return make_response(jsonify({"email": current_user.email, "name": current_user.name}), 200)
    return _profile()
