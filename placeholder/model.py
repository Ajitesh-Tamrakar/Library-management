from datetime import datetime, timedelta
from app import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    available = db.Column(db.Boolean, default=True)
    
    # Define a relationship to Transaction
    transactions = db.relationship('Transaction', backref='book', lazy=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    
    # Define a relationship to Transaction
    transactions = db.relationship('Transaction', backref='user', lazy=True)


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    issue_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    return_date = db.Column(db.DateTime, nullable=True)

    # This method is not strictly needed but can be used for custom return date handling
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.return_date:
            self.return_date = self.issue_date + timedelta(days=15)

    # Optionally, you can create a method to fetch the transaction details
    def to_dict(self):
        return {
            'id': self.id,
            'book_id': self.book_id,
            'user_id': self.user_id,
            'issue_date': self.issue_date,
            'return_date': self.return_date
        }
