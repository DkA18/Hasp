from models import *
from daily import train
from celery import shared_task

@shared_task
def train_model():
    train_model = train()
    model = ModelJSON(data=train_model[0], progress=train_model[1])    
    db.session.add(model)
    db.session.commit()
    return True