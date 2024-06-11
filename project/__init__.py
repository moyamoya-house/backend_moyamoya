from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()

migrate = Migrate()

def create_app(config_filename ="config.py"):
    app= Flask(__name__)
    app.config.from_pyfile(config_filename)
    app.config['DEBUG'] = True
    db.init_app(app)
    migrate.init_app(app)
    
    return app