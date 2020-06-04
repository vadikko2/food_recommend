from mainapp.app import sqlite_db
from flask_login import UserMixin


class User(UserMixin, sqlite_db.Model):
    id = sqlite_db.Column(sqlite_db.Integer, primary_key=True)
    email = sqlite_db.Column(sqlite_db.String(100), unique=True)
    password = sqlite_db.Column(sqlite_db.String(100), unique=False)
    name = sqlite_db.Column(sqlite_db.String(1000), unique=False)
    phone = sqlite_db.Column(sqlite_db.String(12), unique=False, default="")
    confirmed = sqlite_db.Column(sqlite_db.Integer, unique=False)
