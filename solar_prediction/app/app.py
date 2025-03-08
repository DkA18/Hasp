# app.py
import os
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from flask import Flask, jsonify, request, render_template
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
    if not os.path.exists(os.path.join(app.instance_path, 'instance')):
        try:
            os.makedirs(app.instance_path)
        except OSError:
            pass
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath('./instance/db.sqlite')
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
    @app.before_request
    def before_request():
        app.logger.info(f"Request: {request.headers}")
        if 'X-Ingress-Path' in request.headers:
            ingress_path = request.headers['X-Ingress-Path']
            if request.path.startswith(ingress_path):
                request.environ['SCRIPT_NAME'] = ingress_path
                request.path = request.path[len(ingress_path):]

    
    return app

if __name__ == '__main__':
    app = create_app()
    
    app.run(host='0.0.0.0', port=5000, debug=True)
