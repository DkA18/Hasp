# app.py
from flask import Flask, jsonify, request,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import pandas as pd
from network import NeuralNetwork
from views import views
from models import db

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(views, url_prefix="/")
db.init_app(app)
Migrate(app, db)

# influx_client = InfluxDBClient(
#         host="localhost",
#         port=8086,
#         username="homeassist",
#         password="homeassist",
#         database="homeassistant",
#     )



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
