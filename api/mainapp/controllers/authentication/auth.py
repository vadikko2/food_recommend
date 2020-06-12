from flask import Blueprint, jsonify, make_response, render_template
from werkzeug.security import generate_password_hash, check_password_hash
from mainapp.core.users.models import *
from mainapp.core.coockies import *
from sqlalchemy import or_
from flask_login import login_user, logout_user, login_required
from flask_jwt_extended import create_access_token, decode_token
import datetime
from mainapp.core.mail_service import send_email
from mainapp.core.passwords import randomStringDigits

from mainapp.app import logger, db, new_users_logger

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET"])
def login():
    email, password = request.authorization.username.lower(), request.authorization.password
    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return make_response(jsonify({
            "message": f"Please check your login details and try again. Unsuccessful try logging with email {email} "
                       f"and password {password}"}), 401)

    if not user.confirmed:
        return make_response(jsonify({
            "message": f"Please confirm your account. Check {email} email."}), 401)
    login_user(user, remember=True)
    resp = make_response(jsonify({"message": "Successful login"}), 200)
    resp.set_cookie(str(user.id), user.password)
    return resp


@auth.route("/signup", methods=["POST"])
def signup():
    r = request.get_json(force=True)
    try:
        r["email"], r["name"], r["password"]
    except:
        logger.error(f"Incorrect request parameters set. Expected: email, name, password. "
                       f"Gotten:{','.join(r.keys())}")
        return make_response(jsonify({
            "message": f"Incorrect request parameters set. Expected: email, name, password. "
                       f"Gotten:{','.join(r.keys())}"}), 401)

    email, name, password = r["email"].lower(), r["name"], r["password"]

    user = User.query.filter(or_(User.email == email)).first()

    # if this returns a user, then the email already exists in database
    if user:
        return make_response(jsonify({
            "message": f"User with email {email} already exists."}), 401)

    # create new user with the form data. Hash the password so plaintext version isn"t saved.
    new_user = User(email=email, name=name,
                    password=generate_password_hash(password, method="sha256"), confirmed=0)

    sqlite_db.session.add(new_user)
    sqlite_db.session.commit()

    confirm_token = create_access_token(str(new_user.email))
    url = request.host_url + f"confirm?token={confirm_token}"
    send_email("[TasteAssistant] Confirm signup",
               sender="tasteassistantbot@gmail.com",
               recipients=[new_user.email],
               text_body=url,
               html_body=render_template("confirm_user_create.html",
                                         url=url, user=new_user.name)
               )

    return make_response(jsonify({"message": "Successful signup. Please confirm your signup with email."}), 200)


@auth.route("/forgot", methods=["POST"])
def forgot():
    r = request.get_json(force=True)
    try:
        email = r["email"]
    except:
        return make_response(jsonify({
            "message": f"Incorrect request parameters set. Expected: email. "
                       f"Gotten:{','.join(r.keys())}"}), 401)
    user = User.query.filter(User.email == email).first()

    if not user:
        return make_response(jsonify({"message": f"Unknown email address {email}"}), 400)

    expires = datetime.timedelta(hours=24)
    reset_token = create_access_token(str(user.id), expires_delta=expires)
    url = request.host_url + f"reset?token={reset_token}"
    send_email("[TasteAssistant] Reset Your Password",
               sender="tasteassistantbot@gmail.com",
               recipients=[user.email],
               text_body=url,
               html_body=render_template("send_token.html",
                                         url=url, user=user.name)
               )

    return make_response(jsonify({"message": f"Sending email with token to the {user.email}"}), 200)


@auth.route("/confirm")
def confirm():
    try:
        confirm_token = request.args.get("token")
        if not confirm_token:
            raise ValueError("there is no token in the request params.")

        user_email = decode_token(confirm_token)["identity"]

        if not user_email:
            raise ValueError("unsuccessful email extraction from token.")

        user = User.query.filter(User.email == user_email).first()

        if not user:
            raise ValueError(f"unknown user with email {user_email}.")

        if user.confirmed:
            raise ValueError(f"account with {user_email} has been already confirmed.")

        User.query.filter(User.email == user.email).update({"confirmed": 1})

        sqlite_db.session.commit()

    except Exception as e:
        logger.error(f"Account confirm error: {e}")
        return make_response(render_template("token_error.html", error=f"Account confirm error: {e}"), 401)

    new_users_logger.info(f'Новый пользователь: {user.email}', alert=True)
    return make_response(render_template("confirm_successful_status.html", user=user.name, email=user.email), 200)


@auth.route("/reset")
def reset():
    try:
        reset_token = request.args.get("token")
        if not reset_token:
            raise ValueError("there is no token in the request params.")

        user_id = decode_token(reset_token)["identity"]

        if not user_id:
            raise ValueError("unsuccessful id extraction from token.")

        if db.find_all("reset_token", req={"user": user_id, "token": reset_token}):
            raise ValueError("token has been already in used.")

        user = User.query.filter(User.id == user_id).first()

        if not user:
            raise ValueError("Unknown user id.")

        new_password = randomStringDigits()

        User.query.filter(User.id == user_id).update(
            {"password": generate_password_hash(new_password, method="sha256")})

        sqlite_db.session.commit()

        db.easy_add("reset_token", document={"user": user_id, "token": reset_token})

        send_email("[TasteAssistant] Reset Your Password",
                   sender="tasteassistantbot@gmail.com",
                   recipients=[user.email],
                   text_body=new_password,
                   html_body=render_template("reset_pass.html", user=user.name, password=new_password)
                   )

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return make_response(render_template("token_error.html", error=f"Password reset error: {e}"), 401)
    return make_response(render_template("reset_successful_status.html", user=user.name, email=user.email), 200)


@auth.route("/change", methods=["POST"])
@login_required
def change():
    @cookie
    def _change():
        r = request.get_json(force=True)
        try:
            old_password, new_password = r["old"], r["new"]
        except:
            logger.error(f"Incorrect request parameters set. Expected: old, new. "
                                                     f"Gotten: {','.join(r.keys())}")
            return make_response(jsonify({"message": f"Incorrect request parameters set. Expected: old, new. "
                                                     f"Gotten: {','.join(r.keys())}"}), 401)

        if not check_password_hash(current_user.password, old_password):
            return make_response(jsonify({"message": "Incorrect old password"}), 401)

        try:
            User.query.filter(User.id == current_user.id).update(
                {"password": generate_password_hash(new_password, method="sha256")})

            sqlite_db.session.commit()
        except Exception as e:
            logger.error(f"Error during password updating: {e}")
            return make_response(jsonify({"message": f"Error during password updating: {e}"}), 500)

        resp = make_response(jsonify({"message": "Password has benn changed"}), 200)
        resp.set_cookie(str(current_user.id), current_user.password)

        return resp

    return _change()


@auth.route('/drop')
@login_required
def drop():
    logout_user()
    return redirect(url_for('main.'))


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return make_response(jsonify({"message": "Successful logout"}), 200)
