from copy import deepcopy
from flask import json
import requests
import pandas as pd
import numpy as np
from network import NeuralNetwork
from model.layers.dense import Dense, AdamDense
from model.activations.activation import *
from model.losses import *
import numpy as np
from flask import current_app, g
from influx import get_influx_data

import os

def min_max_scale(column):
    return column / 10000

def train():
    try:
        solar = pd.DataFrame(get_influx_data().raw["series"][0]["values"], columns=["time", "mean_value"])
        print("using influx", flush=True)
    except:
        solar = pd.read_csv('./data_daily.csv') 
        print("using csv", flush=True)
    solar["mean_value"] = solar["mean_value"] / 100
    solar = solar.dropna()
    solar['time'] = pd.to_datetime(solar['time'], yearfirst=True, utc=True)

    url = f"https://archive-api.open-meteo.com/v1/archive?latitude=49.7751150&longitude=13.3604831&start_date={solar['time'].min().strftime('%Y-%m-%d')}&end_date={solar['time'].max().strftime('%Y-%m-%d')}&daily=weather_code,temperature_2m_mean,temperature_2m_max,temperature_2m_min,apparent_temperature_mean,apparent_temperature_max,apparent_temperature_min,daylight_duration,sunshine_duration,precipitation_sum,rain_sum,precipitation_hours,snowfall_sum,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration,cloud_cover_mean,cloud_cover_max,cloud_cover_min,dew_point_2m_mean,dew_point_2m_max,dew_point_2m_min,et0_fao_evapotranspiration_sum,relative_humidity_2m_mean,relative_humidity_2m_max,relative_humidity_2m_min,snowfall_water_equivalent_sum,wind_gusts_10m_mean,wind_gusts_10m_min,wind_speed_10m_mean,wind_speed_10m_min,wet_bulb_temperature_2m_mean,wet_bulb_temperature_2m_max,wet_bulb_temperature_2m_min,vapour_pressure_deficit_max&timezone=GMT"


    pred = pd.DataFrame(requests.get(url).json()["daily"])
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
    columns_to_scale = data.columns.drop(["mean_value", "month"])  
    data[columns_to_scale] = data[columns_to_scale].apply(min_max_scale)
    data["month"] = np.cos((np.pi * data["month"]) / 6)
    data = data.dropna()
    data = data.sample(frac=1)
    y = data["mean_value"]
    X = data.drop(["mean_value"], axis=1)
    X = X.to_numpy()
    X =np.reshape(X, (X.shape[0],X.shape[1], 1))
    y = np.reshape(y.to_numpy(), (y.shape[0], 1))
    network = [AdamDense(38,64), Softplus(), AdamDense(64, 128),  Tanh(),  AdamDense(128, 32), NormalizedTanh(),  AdamDense(32, 16), Tanh(),  AdamDense(16, 1), Softplus()]
    n = NeuralNetwork(network)
    # print(X, flush=True)
    trained_n = n.train(mse, mse_prime, X, y, epochs=2000,  learning_rate=0.00001, verbose=False)
    
    return trained_n, json.dumps({"error": n.error_rate, "real_error": n.real_error})

def predict(network, from_time, to_time):
    url = f"https://api.open-meteo.com/v1/forecast?latitude=49.7751150&longitude=13.3604831&start_date={from_time.strftime('%Y-%m-%d')}&end_date={to_time.strftime('%Y-%m-%d')}&daily=weather_code,temperature_2m_mean,temperature_2m_max,temperature_2m_min,apparent_temperature_mean,apparent_temperature_max,apparent_temperature_min,daylight_duration,sunshine_duration,precipitation_sum,rain_sum,precipitation_hours,snowfall_sum,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,shortwave_radiation_sum,et0_fao_evapotranspiration,cloud_cover_mean,cloud_cover_max,cloud_cover_min,dew_point_2m_mean,dew_point_2m_max,dew_point_2m_min,et0_fao_evapotranspiration_sum,relative_humidity_2m_mean,relative_humidity_2m_max,relative_humidity_2m_min,snowfall_water_equivalent_sum,wind_gusts_10m_mean,wind_gusts_10m_min,wind_speed_10m_mean,wind_speed_10m_min,wet_bulb_temperature_2m_mean,wet_bulb_temperature_2m_max,wet_bulb_temperature_2m_min,vapour_pressure_deficit_max&timezone=GMT"


    pred = pd.DataFrame(requests.get(url).json()["daily"])
    pred["date"] = pd.to_datetime(pred["time"])
    pred = pred.drop(["time"], axis=1)
    pred["month"] = pred["date"].dt.month
    pred["day"] = pred["date"].dt.day
    pred["year"] = pred["date"].dt.year
    pred = pred.drop(["date"], axis=1)

    pred = pred.drop(["year", "day", "month"], axis=1)
    pred= pred.apply(min_max_scale)
    # pred["month"] = (pred['month']).apply(lambda x: abs(1 - abs(x - 6) / 5))
    
    X = pred.to_numpy()
    X = np.expand_dims(X, axis=-1)
    result = []
    for x in X:
        result.append(network.predict(x).item() * 100)
    return result