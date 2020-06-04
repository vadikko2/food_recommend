from flask import request, redirect, url_for
from flask_login import current_user


def cookie(f):
    def check_cookie(*args, **kwargs):
        change_pass_checker = check_password()
        if not change_pass_checker:
            return redirect(url_for("auth.drop"))
        result = f(*args, **kwargs)
        return result
    return check_cookie


def check_password():
    '''
    :return: 0 if there are no cookies, -1 if password has been changed,  1 if all right
    '''
    if not (str(current_user.id) in request.cookies) or not (
            request.cookies[str(current_user.id)] == current_user.password):
        return 0
    return 1
