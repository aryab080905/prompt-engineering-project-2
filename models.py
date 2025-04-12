from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Investment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    investment_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float)
    expected_return = db.Column(db.Float)
    years = db.Column(db.Integer)
    start_date = db.Column(db.Date, default=datetime.now().date())
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'investment_type': self.investment_type,
            'amount': self.amount,
            'interest_rate': self.interest_rate,
            'expected_return': self.expected_return,
            'years': self.years,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }