from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_ECHO'] = True  # Logs all SQL queries to the console

db = SQLAlchemy(app)

# Import routes after defining app and db
from routes import *

# Function to initialize the database
def init_db():
    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    # Initialize the database
    init_db()
    
    # Run the application
    app.run(debug=True)
