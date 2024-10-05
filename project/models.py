from datetime import datetime
from flask_login import UserMixin
from project import db
from sqlalchemy.dialects.mysql import DOUBLE

# userテーブル
class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    e_mail = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    prof_image = db.Column(db.String(255), nullable=True)
    second_image = db.Column(db.String(255), nullable=True)
    prof_comment = db.Column(db.String(255), nullable=True)
    
    # relation
    moyamoya = db.relationship('Moyamoya', backref='user', lazy=True)
    sent_messages = db.relationship('Chats', foreign_keys='Chats.send_user_id', backref='sender_by', lazy=True)
    received_messages = db.relationship('Chats', foreign_keys='Chats.receiver_user_id', backref='receiver_by', lazy=True)
    notification = db.relationship('Notification', foreign_keys='Notification.user_id', backref='notify', lazy=True)
    
    def get_id(self):
        return str(self.user_id)

#moyamoyaテーブル 
class Moyamoya(db.Model):
    moyamoya_id = db.Column(db.Integer, primary_key=True)
    moyamoya_post = db.Column(db.String(255), nullable=False)
    hash_tag = db.Column(db.String(255), nullable=True)
    post_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relation
    nice = db.relationship('Nice', backref='moyamoya', lazy=True)

# Followテーブル
class Follow(db.Model):
    follow_id = db.Column(db.Integer, primary_key=True)
    follower_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    followed_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('follower_user_id', 'followed_user_id', name='unique_friendship'),
    )
    
    # relation
    corrent_user = db.relationship('User', foreign_keys=[follower_user_id], backref='friends')
    friend = db.relationship('User', foreign_keys=[followed_user_id])

# chatsテーブル
class Chats(db.Model):
    chat_id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(255), nullable=False)
    send_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    receiver_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    chat_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # relation
    sender = db.relationship('User', foreign_keys=[send_user_id])
    receiver = db.relationship('User', foreign_keys=[receiver_user_id])

# Potsテーブル
class Pots(db.Model):
    pots_id = db.Column(db.Integer, primary_key=True)
    audio_file = db.Column(db.String(255), nullable=False)
    emotion_score = db.Column(db.Float, nullable=True)
    stress_level = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    pots_user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

# Niceテーブル
class Nice(db.Model):
    __tablename__ = 'nice'

    nice_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('moyamoya.moyamoya_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    # relation
    post = db.relationship('Moyamoya', foreign_keys=[post_id], backref=db.backref('nices', lazy=True))
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('nices', lazy=True))

    # Unique constraint to prevent duplicate likes by the same user on the same post
    __table_args__ = (
        db.UniqueConstraint('post_id', 'user_id', name='unique_user_post_like'),
    )

    def __repr__(self):
        return f"<Nice(nice_id={self.nice_id}, post_id={self.post_id}, user_id={self.user_id})>"
    

class Bookmark(db.Model):
    __tablename__ = 'bookmark'
    
    bookmark_id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('moyamoya.moyamoya_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    # relation
    post = db.relationship('Moyamoya', foreign_keys=[post_id])
    user = db.relationship('User', foreign_keys=[user_id])


class Notification(db.Model):
    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
    notification = db.Column(db.String(255),nullable=False)
    create_at = db.Column(db.DateTime, nullable=False)

