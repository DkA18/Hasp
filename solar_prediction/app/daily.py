from copy import deepcopy
from flask import json
import requests
import pandas as pd
import numpy as np
from network import NeuralNetwork
from model.layers.dense import Dense, AdamDense
from model.activations.activation import Sigmoid, Tanh, ReLU, LReLU, NormalizedTanh, Softplus, Swish
from model.losses import *
import numpy as np
from flask import current_app, g
from influx import InfluxDBConnector

import os


def train():
    with open("/data/options.json") as f:
        ha_options= json.load(f)
    i = InfluxDBConnector(ha_options["influx_host"], ha_options["influx_port"], ha_options["influx_user"], ha_options["influx_password"], ha_options["influx_db"])
    i.connect()
    try:
        test_query = """SELECT max("value") AS "mean_value" FROM "homeassistant"."autogen"."kWh" WHERE "entity_id"='today_s_pv_generation' GROUP BY time(1d) FILL(0)"""
        test_result = i.query_data(test_query)
        solar = pd.DataFrame(test_result.raw["series"][0]["values"], columns=["time", "mean_value"])
    except Exception as e:
        current_app.logger.error(f"Test query failed: {e}")
    solar['time'] = pd.to_datetime(solar['time'], yearfirst=True, utc=True)


    url = f"https://archive-api.open-meteo.com/v1/archive?latitude=49.7751150&longitude=13.3604831&start_date={solar['time'].min().strftime('%Y-%m-%d')}&end_date={solar['time'].max().strftime('%Y-%m-%d')}&daily=weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,daylight_duration,sunshine_duration,uv_index_max,uv_index_clear_sky_max,precipitation_sum,rain_sum,showers_sum,snowfall_sum,precipitation_hours,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration&timezone=GMT"


    pred = pd.DataFrame(requests.get(url).json()["daily"])
    pred = pred.drop(["sunrise", "sunset", "uv_index_max", "uv_index_clear_sky_max", "showers_sum", "precipitation_probability_max"], axis=1)
    pred["date"] = pd.to_datetime(pred["time"])
    pred = pred.drop(["time"], axis=1)
    pred["month"] = pred["date"].dt.month
    pred["day"] = pred["date"].dt.day
    pred["year"] = pred["date"].dt.year
    pred = pred.drop(["date"], axis=1)
    solar["day"] = solar["time"].dt.day
    solar["month"] = solar["time"].dt.month
    solar["year"] = solar["time"].dt.year
    solar = solar.drop(["time"], axis=1)
    data = pd.merge(pred, solar, on=["day", "month", "year"], how="inner")
    data = data.drop(["year", "day"], axis=1)
    data = data/10000
    data["month"] = (data['month'] * 10000).apply(lambda x: abs(1 - abs(x - 6) / 5))
    data = data.sample(frac=1)
    data['mean_value'] = data['mean_value'].fillna(0)
    data=  data.dropna()
    y = data["mean_value"]
    X = data.drop(["mean_value"], axis=1)
    X = X.to_numpy()
    X =np.reshape(X, (X.shape[0],X.shape[1], 1))
    y = np.reshape(y.to_numpy(), (y.shape[0], 1))
    network = [Dense(17,32), Softplus(), AdamDense(32, 64),  NormalizedTanh(),  AdamDense(64, 128),  Tanh(),  AdamDense(128, 1), Softplus()]

    n = NeuralNetwork(network)
    # print(X, flush=True)
    trained_n = n.train(mse, mse_prime, X, y, epochs=2000, learning_rate=0.00001, verbose=False)
    
    return trained_n, json.dumps({"error": n.error_rate, "real_error": n.real_error})

def predict(network, from_time, to_time):
    url = f"https://api.open-meteo.com/v1/forecast?latitude=49.7751150&longitude=13.3604831&start_date={from_time.strftime('%Y-%m-%d')}&end_date={to_time.strftime('%Y-%m-%d')}&daily=weather_code,temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,sunrise,sunset,daylight_duration,sunshine_duration,uv_index_max,uv_index_clear_sky_max,precipitation_sum,rain_sum,showers_sum,snowfall_sum,precipitation_hours,precipitation_probability_max,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration&timezone=GMT"


    pred = pd.DataFrame(requests.get(url).json()["daily"])
    pred = pred.drop(["sunrise", "sunset", "uv_index_max", "uv_index_clear_sky_max", "showers_sum", "precipitation_probability_max"], axis=1)
    pred["date"] = pd.to_datetime(pred["time"])
    pred = pred.drop(["time"], axis=1)
    pred["month"] = pred["date"].dt.month
    pred["day"] = pred["date"].dt.day
    pred["year"] = pred["date"].dt.year
    pred = pred.drop(["date"], axis=1)

    pred = pred.drop(["year", "day"], axis=1)
    pred = pred/10000
    pred["month"] = (pred['month'] * 10000).apply(lambda x: abs(1 - abs(x - 6) / 5))
    X = pred.to_numpy()
    X = np.expand_dims(X, axis=-1)
    # print(X, flush=True)
    result = []
    for x in X:
        result.append(network.predict(x).item()* 10000)
    return result