import datetime
from models import *
from daily import train
from celery import shared_task

@shared_task
def train_model(name: str, type: int):
    train_model = train()
    model = ModelJSON(data=train_model[0], progress=train_model[1], name=name, model_type=type)    
    db.session.add(model)
    db.session.commit()
    return True

@shared_task
def cache_daily_predictions(predictions: dict, model_id: int):
    for date, value in predictions.items():
        date=datetime.datetime.strptime(date, "%Y-%m-%d")
        db_prediction = PredictionValues.query.filter(db.func.date(PredictionValues.date) == date.date(), PredictionValues.model_id == model_id).first()
        if db_prediction:
            db_prediction.value = value
        else:
            prediction = PredictionValues(date=date, value=value, model_id=model_id)
            db.session.add(prediction)
    db.session.commit()
    return True
    
    