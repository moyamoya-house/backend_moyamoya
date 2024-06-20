from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import os

db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

cors = CORS()

jwt = JWTManager()

def create_app(config_filename ="config.py"):
    app= Flask(__name__)
    app.config.from_pyfile(config_filename)
    app.config['DEBUG'] = True
    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    
    app.config['JWT_SECRET_KEY'] = 'moyamoya_house'
    
    from project.models import User, Pots, Moyamoya, Chats, Follow
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from project.views import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app