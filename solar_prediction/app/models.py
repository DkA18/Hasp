from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class PredictionValues(db.Model):
    __tablename__ = 'prediction_values'
    id = db.Column(db.Integer, primary_key=True)  
    date = db.Column(db.Date, nullable=False, index=True) 
    value = db.Column(db.Float, nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('model_json.id'), nullable=False)
    model = db.relationship('ModelJSON', backref=db.backref('predictions', lazy=True, cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<PredictionValues(date={self.date}, value={self.value})>"

class ModelJSON(db.Model):
    __tablename__ = 'model_json'
    id = db.Column(db.Integer, primary_key=True)  
    name = db.Column(db.String(255), nullable=False, unique=True)
    model_type = db.Column(db.Integer, nullable=False) # 1 for daily, 2 for hourly
    data = db.Column(db.JSON, nullable=False)  
    progress = db.Column(db.JSON, nullable=False)  

    def __repr__(self):
        return f"<ModelJSON(id={self.id}, data={self.data})>"