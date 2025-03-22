from datetime import datetime, timedelta
from flask import Blueprint, abort, json, redirect, request, jsonify, current_app, url_for
import pandas as pd
from models import *
from daily import predict
from network import NeuralNetwork
from influx import InfluxDBConnector
from tasks import cache_daily_predictions, train_model
from celery.result import AsyncResult

api = Blueprint('api', __name__)


@api.route("/change_date", methods=["POST"])
def index_daily_change_date():
    date_range = request.json.get("date_range")
    model_id = request.json.get("model_id")
    if not date_range or not model_id:
        return abort(400)
    date_range = date_range.split(" to ") if "to" in date_range else [date_range, date_range]
    try:
        date_from = datetime.strptime(date_range[0], "%Y-%m-%d")
        date_to = datetime.strptime(date_range[1], "%Y-%m-%d")
    except ValueError:
        return abort(400)
    
    with open("/data/options.json") as f:
        ha_options= json.load(f)
    i = InfluxDBConnector(ha_options["influx_host"], ha_options["influx_port"], ha_options["influx_user"], ha_options["influx_password"], ha_options["influx_db"])
    i.connect()
    try:
        test_query = f"""SELECT max("value") AS "mean_value" FROM "homeassistant"."autogen"."kWh" WHERE time > {date_from.strftime('%Y-%m-%dT%H:%M:%SZ')} AND time < {date_to.strftime('%Y-%m-%dT%H:%M:%SZ')} AND "entity_id"='today_s_pv_generation' GROUP BY time(1d) FILL(0)"""
        test_result = i.query_data(test_query)
        solar = list(pd.DataFrame(test_result.raw["series"][0]["values"], columns=["time", "mean_value"])["mean_value"])
    except Exception as e:
        current_app.logger.error(f"Test query failed: {e}")
    
    model = ModelJSON.query.get(model_id)
    if not model:
        return abort(404, description="Model not found")
        
    network = NeuralNetwork()
    network.load(model.data)
    
    existing_predictions = PredictionValues.query.filter((db.func.date(PredictionValues.date) >= date_from.date()) & (db.func.date(PredictionValues.date) <= date_to.date())).all()
    if len(existing_predictions) == (date_to - date_from).days + 1:
        predictions = [pred.value for pred in existing_predictions]
        current_app.logger.info("Using cached predictions")
    else:
        predictions = predict(network, date_from, date_to)
        cache_daily_predictions.delay(dict(zip([(datetime.today() + timedelta(days=i)).strftime("%Y-%m-%d")  for i in range(5)],predictions)),model.id  ) 
        current_app.logger.info("Using new predictions") 
   
    date_labels = [(date_from + timedelta(days=i)).strftime("%B %d, %Y") for i in range((date_to - date_from).days + 1)]
    response = jsonify({"predictions": predictions, "labels": date_labels, "actual": solar})
    response.set_cookie("selected_model", model_id, max_age=30*24*60*60)
    return response

@api.route("/create_model", methods=["POST"])
def create_model():
    name = request.form.get("name")
    model_type = request.form.get("type")
    
    if not name or not model_type:
        return abort(400, description="Missing model name or type")
    
    existing_model = ModelJSON.query.filter_by(name=name).first()
    if existing_model:
        return jsonify({"message": "Model already exists"}), 400

    task = train_model.delay(name, 1 if model_type == "daily" else 2)
    print(AsyncResult(task.task_id).state, flush=True)
    
    return redirect(url_for("views.index"))


