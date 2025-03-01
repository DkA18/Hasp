from copy import copy, deepcopy
from datetime import datetime
import datetime as dt
from flask import Blueprint, abort, redirect, render_template, request, url_for, jsonify
from models import *
from daily import predict
from network import NeuralNetwork
from tasks import train_model

views = Blueprint("views", __name__)
api = Blueprint('api', __name__)

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
        case _:
            return abort(404)
        
@api.route("/change_date", methods=["POST"])
def index_daily_change_date():
    date_range = request.json.get("date_range")
    if not date_range:
        return abort(400)
    date_range = date_range.split(" to ") if "to" in date_range else [date_range, date_range]
    try:
        date_from = datetime.strptime(date_range[0], "%Y-%m-%d")
        date_to = datetime.strptime(date_range[1], "%Y-%m-%d")
    except ValueError:
        return abort(400)
    
    models = ModelJSON.query.all()
    
    model = models[0]
        
    network = NeuralNetwork()
    network.load(model.data)
    
    return jsonify(predict(network, date_from, date_to))
    

def index():
    models = ModelJSON.query.all()
    # train_model.delay()
    # if not models:
    # else:
    model = models[0]
        
    network = NeuralNetwork()

    network.load(model.data)
    
    result = predict(network, datetime.today(), datetime.today() + dt.timedelta(days=4))
    
    return render_template("index.html", model=True, result=result)


def settings():
    return render_template("settings.html")
    
