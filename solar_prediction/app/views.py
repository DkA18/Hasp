from copy import copy, deepcopy
from datetime import datetime, timedelta
import datetime as dt
from flask import Blueprint, abort, redirect, render_template, request, url_for, jsonify, current_app
from models import *
from daily import predict
from network import NeuralNetwork
from tasks import train_model, cache_daily_predictions

views = Blueprint("views", __name__)

@views.route("/favicon.ico")
def favicon():
    return redirect(url_for("static", filename="favicon.ico"))

@views.route("/")
def default():
    return redirect(url_for("views.base", page='index'))

@views.route('/&page=<page>')
def base(page: str):
    match page:
        case 'index':
            return index()
        case 'settings':
            return settings()
        case 'models':
            return models()
        case _:
            return abort(404)
        
def models():
    return render_template("models.html", models=ModelJSON.query.all())
    

def index():
    models = ModelJSON.query.all()
    if not models:
        # train_model.delay()
        return render_template("index.html", exists=False)
    else:
        model = models[0]
        
    network = NeuralNetwork()

    network.load(model.data)
    
    date_from = datetime.today()
    date_to = datetime.today() + dt.timedelta(days=4)
    
    existing_predictions = PredictionValues.query.filter(db.func.date(PredictionValues.date )>= date_from.date(), db.func.date(PredictionValues.date )<= date_to.date()).all()
    
    if len(existing_predictions) == (date_to - date_from).days + 1:
        predictions = [pred.value for pred in existing_predictions]
        current_app.logger.info("Using cached predictions")
    else:
        predictions = predict(network, date_from, date_to)
        cache_daily_predictions.delay(dict(zip([(datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d")  for i in range(5)],predictions)), model.id  ) 
        current_app.logger.info("Using new predictions") 
    
    
    labels = [(datetime.today() + timedelta(days=i)).strftime("%B %d, %Y") for i in range(5)]
    
    
    
    return render_template("index.html",exists=True,  result=predictions, labels=labels, models=[model.name for model in models])


def settings():
    return render_template("settings.html")
    
