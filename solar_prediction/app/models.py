from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PredictionValues(db.Model):
    __tablename__ = 'prediction_values'
    id = db.Column(db.Integer, primary_key=True)  
    date = db.Column(db.Date, nullable=False, index=True) 
    value = db.Column(db.Float, nullable=False)  

    def __repr__(self):
        return f"<PredictionValues(date={self.date}, value={self.value})>"

class ModelJSON(db.Model):
    __tablename__ = 'model_json'
    id = db.Column(db.Integer, primary_key=True)  
    data = db.Column(db.JSON, nullable=False)  
    progress = db.Column(db.JSON, nullable=False)  

    def __repr__(self):
        return f"<ModelJSON(id={self.id}, data={self.data})>"