from datetime import datetime
from flask_login import UserMixin
from project import db


class User(db.Model,UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), unique=True , nullable=False)
    password = db.Column(db.String(255), nullable=False)
    e_mail = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime , default= datetime.utcnow)
    prof_image = db.Column(db.String(255), nullable=True)