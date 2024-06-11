from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()

migrate = Migrate()

def create_app():
    app= Flask(__name__)
    