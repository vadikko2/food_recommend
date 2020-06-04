import json

import requests
import hashlib
from flask import jsonify, make_response, request
from mainapp.app import cache, db, PHONE_NUMBER, BILL_PASS
from mainapp.core.coockies import cookie
from flask import Blueprint
from flask_login import login_required, current_user
import datetime

# t=20200215T2135&s=5368.00&fn=9280440300221450&i=4019&fp=2551064581&n=1

bills_headers = {"device-id": "", "device-os": ""}
bills = Blueprint("bills", __name__)


@bills.route("/bills/verify", methods=["GET"])
@login_required
def verify():
    @cookie
    def _verify():
        if sorted(request.args) != sorted(["t", "s", "i", "fn", "fp", "n"]):
            return make_response(jsonify({
                "message": f"Incorrect request parameters set. Expected: t, s, fn, i, fp, n. "
                           f"Gotten:{','.join(request.args)}"}), 401)
        bill_verify_request = f"https://proverkacheka.nalog.ru:9999/v1/ofds/*/inns/*/" \
                              f"fss/{request.args.get('fn')}" \
                              f"/operations/{request.args.get('n')}" \
                              f"/tickets/{request.args.get('i')}?" \
                              f"fiscalSign={request.args.get('fp')}&" \
                              f"date={datetime.datetime.strptime(request.args.get('t'), '%Y%m%dT%H%M').strftime('%Y-%m-%dT%H:%M:%S')}&" \
                              f"sum={int(float(request.args.get('s')) * 100)}"

        verify_status = requests.get(bill_verify_request, headers=bills_headers)
        if verify_status.status_code == 204:
            return make_response(jsonify({"message": "Success verify."}), 200)
        elif verify_status.status_code == 406:
            return make_response(jsonify({"message": "Bill not found or incorrect date or sum parameters."}), 406)
        else:
            return make_response(verify_status.content, verify_status.status_code)

    return _verify()


@bills.route("/bills/info", methods=["GET"])
@login_required
def info():
    @cookie
    def _info():
        if not sorted(request.args) == sorted(["t", "s", "i", "fn", "fp", "n"]):
            return make_response(jsonify({
                "message": f"Incorrect request parameters set. Expected: t, s, fn, i, fp, n. "
                           f"Gotten:{','.join(request.args)}"}), 401)

        bill_info_req = f"https://proverkacheka.nalog.ru:9999/v1/inns/*/kkts/*/fss/{request.args.get('fn')}" \
                        f"/tickets/{request.args.get('i')}?" \
                        f"fiscalSign={request.args.get('fp')}&sendToEmail=no"

        info_status = requests.get(bill_info_req, headers=bills_headers,
                                   auth=(PHONE_NUMBER, BILL_PASS))

        if info_status.status_code == 200:
            bill = info_status.json()

            try:
                bill_id, message = dump_bill(current_user.id, bill)
            except Exception as e:
                return make_response(str(ValueError(f'Ошибка записи чека в базу данных: {e}')), 500)

            return make_response(jsonify({"message": message, "id": bill_id}), 200)
        else:
            return make_response(
                jsonify({"message": f'Error: {info_status.content.decode()}. Probably bill has not been verified.'}),
                info_status.status_code)

    return _info()


@bills.route("/bills/pagination", methods=["GET"])
@login_required
@cache.cached(query_string=True, timeout=500)
def pagination():
    @cookie
    def _pagination():
        skip = request.args.get("skip", default=0, type=int)
        limit = request.args.get("limit", default=10, type=int)

        if not all([isinstance(skip, int), isinstance(limit, int), not skip < 0, not limit < 0]):
            return make_response(jsonify({
                "message": f"Incorrect [skip] and [limit] request params"}), 401)

        bills = db.aggregation('bills',
                               [{"$match": {"user": current_user.id}},
                                {"$group": {
                                    "_id": {
                                        "id": "$checksum",
                                        "datetime": "$bill.document.receipt.dateTime",
                                        "price": "$bill.document.receipt.totalSum"
                                    }
                                }
                                },
                                {"$skip": skip}, {"$limit": limit}])

        for i, bill in enumerate(bills):
            bills[i]['metric'] = datetime.datetime.fromisoformat(bill['datetime']).timestamp()

        response = {"previews": bills, "sort_option": -1}
        return make_response(response, 200)

    return _pagination()


@bills.route("/bills/<bill>", methods=["GET"])
@login_required
@cache.cached(query_string=True, timeout=500)
def get_bill(bill):
    @cookie
    def _bill(bill):

        if not bill: return make_response(jsonify({
            "message": f"Incorrect request params."}), 401)

        try:
            bill = db.find_one('bills', {"checksum": bill})
        except Exception as e:
            make_response(jsonify({"message": f'Ошибка при обращении к базе данных {str(e)}'}, 500))

        if not bill: return make_response(jsonify({"message": "BIll not found."}), 404)

        response = {
            "price": bill['bill']['document']['receipt']['totalSum'],
            "components": list(map(lambda x: {
                'name': x.get('name'),
                'price': x.get('price'),
                'quantity': x.get('quantity'),
                'sum': x.get('sum')
            }, bill['bill']['document']['receipt']['items'])),
            "timestamp": bill['bill']['document']['receipt']['dateTime']
        }
        return make_response(response, 200)

    return _bill(bill)


def dump_bill(user_id, data):
    checksum = hashlib.md5(str.encode(json.dumps(data, sort_keys=True))).hexdigest()
    try:
        saved = db.add('bills', {"user": user_id, "checksum": checksum, "bill": data})
        return checksum, 'Новый чек был сохранен!' if saved else 'Этот чек уже отсканирован!'
    except Exception as e:
        raise ValueError(f'Ошибка сохранения в базу чека {checksum}: {e}')
