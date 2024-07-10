from datetime import datetime
from flask_login import UserMixin
from project import db
from sqlalchemy.dialects.mysql import DOUBLE

# userテーブル
class User(db.Model,UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), unique=True , nullable=False)
    password = db.Column(db.String(255), nullable=False)
    e_mail = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime , default= datetime.utcnow)
    prof_image = db.Column(db.String(255), nullable=True)
    second_image = db.Column(db.String(255), nullable=True)
    prof_comment = db.Column(db.String(255), nullable=True)
    
    # relation
    moyamoya = db.relationship('Moyamoya', backref='user',lazy=True)
    sent_messages = db.relationship('Chats', foreign_keys='Chats.send_user_id', backref='sender_by', lazy=True)
    received_messages = db.relationship('Chats', foreign_keys='Chats.receiver_user_id', backref='receiver_by', lazy=True)
    
    def get_id(self):
        return str(self.user_id)

#moyamoyaテーブル 
class Moyamoya(db.Model):
    moyamoya_id = db.Column(db.Integer, primary_key=True)
    moyamoya_post = db.Column(db.String(255), nullable=False)
    post_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Followテーブル
class Follow(db.Model):
    follow_id = db.Column(db.Integer, primary_key=True)
    follower_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    followed_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    db.UniqueConstraint('follower_user_id','followed_user_id',name='unique_friendship')
    
    # relation
    corrent_user = db.relationship('User',foreign_keys=[follower_user_id], backref='friends')
    friend = db.relationship('User', foreign_keys=[followed_user_id])

# chatsテーブル
class Chats(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    send_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    receiver_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    chat_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relation
    sender = db.relationship('User',foreign_keys=[send_user_id])
    receiver = db.relationship('User',foreign_keys=[receiver_user_id])

# Potsテーブル
class Pots(db.Model):
    pots_id = db.Column(db.Integer, primary_key=True)
    audio_file = db.Column(db.String(255),nullable=False)
    emotion_score = db.Column(DOUBLE, nullable=True)
    stress_level = db.Column(DOUBLE, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pots_user_id = db.Column(db.Integer,db.ForeignKey('user.user_id'), nullable=False)
