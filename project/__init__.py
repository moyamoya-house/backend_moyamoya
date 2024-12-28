from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
import os
from datetime import timedelta
import eventlet
from dotenv import load_dotenv

db = SQLAlchemy()

migrate = Migrate()

login_manager = LoginManager()

cors = CORS()

jwt = JWTManager()

socket = SocketIO()

load_dotenv()

def create_app(config_filename ="config.py"):
    app= Flask(__name__)
    app.config.from_pyfile(config_filename)
    app.config['DEBUG'] = True
    db.init_app(app)
    migrate.init_app(app,db)
    login_manager.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    socket.init_app(app, cors_allowed_origins="*")
# Ensure the upload folder path is correct
    app.config["UPLOAD_FOLDER"] = os.path.join(os.getcwd(), 'project/static/prof_image/')
    app.config["UPLOAD_FOLDER_SECOND"] = os.path.join(os.getcwd(), 'project/static/second_prof_image')
    app.config["UPLOAD_FOLDER_GROUP"] = os.path.join(os.getcwd(), 'project/static/group_chat')
    app.config["UPLOAD_FOLDER_AUDIO"] = os.path.join(os.getcwd(), 'project/static/audio_file')
    app.config["UPLOAD_FOLDER_CHAT"] = os.path.join(os.getcwd(), 'project/static/chat_image')
    
    app.config['SECRET_KEY'] = 'moyamoya_house'
    app.config['JWT_SECRET_KEY'] = 'moyamoya_house'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
    
    from project.models import User, Pots, Moyamoya, Chats, Follow, Nice
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from project.views import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app