import pytest
from datetime import date, timedelta
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models import (
    User, Destination, Attraction, Package,
    Hotel, Room, Booking, Payment, Review
)

@pytest.fixture(scope='session')
def app():
    app = create_app('testing')
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    with app.app_context():
        db.create_all()

        # Seed basic baseline test entities
        admin = User(
            full_name='Test Admin',
            email='admin@test.com',
            phone='1234567890',
            role='admin'
        )
        admin.set_password('Admin@123')

        customer = User(
            full_name='Test Customer',
            email='customer@test.com',
            phone='9876543210',
            role='customer'
        )
        customer.set_password('Cust@123')

        dest = Destination(
            name='Ooty Test',
            country='India',
            region='Tamil Nadu',
            category='Hill Station',
            description='Test destination description',
            image_url='https://example.com/ooty.jpg',
            estimated_budget=Decimal('15000.00'),
            is_active=True
        )

        db.session.add_all([admin, customer, dest])
        db.session.commit()

        # Add package
        pkg = Package(
            destination_id=dest.id,
            name='Ooty Heritage Tour',
            description='Test package description',
            duration_days=3,
            price_per_person=Decimal('5000.00'),
            inclusions='Hotel, Breakfast',
            is_active=True
        )

        # Add hotel & room
        hotel = Hotel(
            destination_id=dest.id,
            name='Ooty Grand Palace',
            address='123 Tea Garden Road',
            description='Test hotel description',
            amenities='WiFi, Spa',
            rating=Decimal('4.8'),
            is_active=True
        )
        db.session.add_all([pkg, hotel])
        db.session.commit()

        room = Room(
            hotel_id=hotel.id,
            room_type='Deluxe King',
            capacity=2,
            price_per_night=Decimal('3000.00'),
            total_rooms=2,  # limited to 2 rooms to test availability & concurrency
            is_active=True
        )
        db.session.add(room)
        db.session.commit()

        yield db.session

        db.session.remove()
        db.drop_all()

@pytest.fixture
def auth_client(client, db_session):
    client.post('/login', data={
        'email': 'customer@test.com',
        'password': 'Cust@123'
    }, follow_redirects=True)
    return client

@pytest.fixture
def admin_client(client, db_session):
    client.post('/login', data={
        'email': 'admin@test.com',
        'password': 'Admin@123'
    }, follow_redirects=True)
    return client
