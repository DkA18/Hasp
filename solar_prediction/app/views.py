from datetime import datetime
import datetime as dt
from flask import Blueprint, Response, abort, redirect, render_template, request, url_for
from models import *
from daily import train, predict
from network import NeuralNetwork

views = Blueprint("views", __name__)

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

def index():
    models = ModelJSON.query.all()
    # print(models, flush=True)
    if not models:
        train_model = train()
        model = ModelJSON(data=train_model)    
        db.session.add(model)
        db.session.commit()
    else:
        model = models[0]
        
    network = NeuralNetwork()
    network.load(model.data)
    
    result = predict(network, datetime.today(), datetime.today() + dt.timedelta(days=4))
    
    return render_template("index.html", model=True, result=result)

def settings():
    return render_template("settings.html")
    
