from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import pytz
import logging

# Initialize Flask app
app = Flask(__name__)

# Configure SQLite database (file-based for persistence)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fitness_studio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('fitness_studio')

# Timezone for classes (IST)
IST = pytz.timezone('Asia/Kolkata')

# Models
class FitnessClass(db.Model):
    __tablename__ = 'fitness_classes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    datetime_ist = db.Column(db.DateTime, nullable=False)  # Stored in IST timezone
    instructor = db.Column(db.String(50), nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    def to_dict(self, target_tz=None):
        # Convert datetime from IST to target timezone if provided
        dt = IST.localize(self.datetime_ist)
        if target_tz:
            dt = dt.astimezone(target_tz)
        return {
            'id': self.id,
            'name': self.name,
            'datetime': dt.isoformat(),
            'instructor': self.instructor,
            'available_slots': self.available_slots
        }

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('fitness_classes.id'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(100), nullable=False)

    fitness_class = db.relationship('FitnessClass', backref=db.backref('bookings', lazy=True))

# Create tables and seed data
with app.app_context():
    db.create_all()

    # Seed data if no classes exist
    if FitnessClass.query.count() == 0:
        from datetime import timedelta

        now_ist = datetime.now(IST).replace(tzinfo=None)
        classes = [
            FitnessClass(
                name='Yoga',
                datetime_ist=now_ist + timedelta(days=1, hours=9),
                instructor='Alice',
                available_slots=10
            ),
            FitnessClass(
                name='Zumba',
                datetime_ist=now_ist + timedelta(days=2, hours=18),
                instructor='Bob',
                available_slots=15
            ),
            FitnessClass(
                name='HIIT',
                datetime_ist=now_ist + timedelta(days=3, hours=7),
                instructor='Charlie',
                available_slots=12
            ),
        ]
        db.session.bulk_save_objects(classes)
        db.session.commit()

# Simple route to check API status
@app.route('/')
def index():
    return jsonify({'message': 'Fitness Studio Booking API is running'})

# GET /classes endpoint
@app.route('/classes', methods=['GET'])
def get_classes():
    # Get timezone from query parameter, default to IST if not provided
    tz_name = request.args.get('timezone', 'Asia/Kolkata')
    try:
        target_tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        return jsonify({'error': 'Invalid timezone'}), 400

    classes = FitnessClass.query.all()
    result = [cls.to_dict(target_tz) for cls in classes]
    return jsonify(result)

# POST /book endpoint
@app.route('/book', methods=['POST'])
def book_class():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Missing JSON body'}), 400

    class_id = data.get('class_id')
    client_name = data.get('client_name')
    client_email = data.get('client_email')

    # Basic input validation
    if not class_id or not client_name or not client_email:
        return jsonify({'error': 'Missing required fields'}), 400

    fitness_class = FitnessClass.query.get(class_id)
    if not fitness_class:
        return jsonify({'error': 'Fitness class not found'}), 404

    if fitness_class.available_slots <= 0:
        return jsonify({'error': 'No available slots'}), 400

    # Create booking
    booking = Booking(class_id=class_id, client_name=client_name, client_email=client_email)
    try:
        fitness_class.available_slots -= 1
        db.session.add(booking)
        db.session.commit()
        logger.info(f"Booking successful for class_id={class_id} by {client_email}")
        return jsonify({'message': 'Booking successful'})
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Database error occurred'}), 500

# GET /bookings endpoint
@app.route('/bookings', methods=['GET'])
def get_bookings():
    client_email = request.args.get('email')
    if not client_email:
        return jsonify({'error': 'Missing email query parameter'}), 400

    bookings = Booking.query.filter_by(client_email=client_email).all()
    result = []
    for booking in bookings:
        fitness_class = booking.fitness_class
        result.append({
            'booking_id': booking.id,
            'class_id': fitness_class.id,
            'class_name': fitness_class.name,
            'datetime': IST.localize(fitness_class.datetime_ist).isoformat(),
            'instructor': fitness_class.instructor,
            'client_name': booking.client_name,
            'client_email': booking.client_email
        })
    return jsonify(result)

if __name__ == '__main__':
    print("Starting Fitness Studio Booking API...")
    app.run(debug=True, host='127.0.0.1', port=5000)
