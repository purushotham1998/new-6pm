import os
import logging
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from wtforms import Form, StringField, IntegerField, validators
from logging.config import dictConfig

# Load environment variables
load_dotenv()

# Configure structured logging
dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        },
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Add security headers
Talisman(app)

# Enable CSRF protection
csrf = CSRFProtect(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    locality = db.Column(db.String(100), nullable=False)

class UserForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=100)])
    age = IntegerField('Age', [validators.NumberRange(min=0)])
    sex = StringField('Sex', [validators.AnyOf(['Male', 'Female'])])
    mobile_number = StringField('Mobile Number', [validators.Length(min=10, max=15)])
    experience = IntegerField('Experience', [validators.NumberRange(min=0)])
    locality = StringField('Locality', [validators.Length(min=1, max=100)])

@app.route('/register', methods=['POST'])
def register_user():
    form = UserForm(request.form)
    if form.validate():
        new_user = User(
            name=form.name.data,
            age=form.age.data,
            sex=form.sex.data,
            mobile_number=form.mobile_number.data,
            experience=form.experience.data,
            locality=form.locality.data
        )
        db.session.add(new_user)
        db.session.commit()
        app.logger.info(f"User {new_user.name} registered successfully!")
        return jsonify({'message': 'User registered successfully!'}), 201
    else:
        app.logger.info(f"Form errors: {form.errors}")
        return jsonify({'errors': form.errors}), 400

@app.route('/users', methods=['GET'])
def get_users():
    filters = request.args
    query = User.query

    if 'name' in filters:
        query = query.filter(User.name.like(f"%{filters['name']}%"))
    if 'age' in filters:
        query = query.filter_by(age=filters['age'])
    if 'sex' in filters:
        query = query.filter_by(sex=filters['sex'])
    if 'locality' in filters:
        query = query.filter(User.locality.like(f"%{filters['locality']}%"))

    users = query.all()
    user_list = [
        {
            'id': user.id,
            'name': user.name,
            'age': user.age,
            'sex': user.sex,
            'mobile_number': user.mobile_number,
            'experience': user.experience,
            'locality': user.locality
        } for user in users
    ]
    app.logger.info(f"Found {len(user_list)} users")
    return jsonify(user_list)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add-sample-data', methods=['POST'])
def add_sample_data():
    sample_users = [
        User(name='John Doe', age=30, sex='Male', mobile_number='1234567890', experience=5, locality='New York'),
        User(name='Jane Smith', age=25, sex='Female', mobile_number='9876543210', experience=3, locality='Los Angeles'),
        User(name='Alice Johnson', age=35, sex='Female', mobile_number='5556667777', experience=10, locality='Chicago'),
        User(name='Bob Brown', age=40, sex='Male', mobile_number='4445556666', experience=15, locality='Houston')
    ]
    db.session.bulk_save_objects(sample_users)
    db.session.commit()
    app.logger.info('Sample data added successfully!')
    return jsonify({'message': 'Sample data added successfully!'}), 201

@app.errorhandler(404)
def not_found_error(error):
    app.logger.info('Resource not found')
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.info('An internal error occurred')
    return jsonify({'error': 'An internal error occurred'}), 500

@app.before_request
def log_request_info():
    app.logger.info(f"Request: {request.method} {request.url}")

if __name__ == '__main__':
    app.run(debug=True)