# app.py
import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask, json, jsonify, request, render_template, url_for, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
from network import NeuralNetwork
from worker import celery_init_app
from views import views
from api import api
from models import db

celery = None

def create_app():
    global celery
    app = Flask(__name__)
    if not os.path.exists("/data/instance"):
        try:
            os.makedirs("/data/instance")
        except OSError:
            pass
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////data/instance/db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    app.config.from_mapping(
    CELERY=dict(
        broker_url="redis://localhost",
        result_backend="redis://localhost",
        task_ignore_result=True,
    ),
)
    worker = celery_init_app(app)
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(api, url_prefix="/api")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    migrate = Migrate(app, db)  # Ensure Migrate is initialized with app and db
        
    def custom_url_for(endpoint, **values):
        ingress_path = request.headers.get("X-Ingress-Path", "")
        url = url_for(endpoint, **values)
        if ingress_path and not url.startswith(ingress_path):
            url = f"{ingress_path}{url}"

        return url
    
    app.jinja_env.globals['url_for'] = custom_url_for
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
