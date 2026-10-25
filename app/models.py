from datetime import datetime
from decimal import Decimal
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db, login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='customer', nullable=False)  # 'customer' or 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    bookings = db.relationship('Booking', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')
    favourites = db.relationship('Favourite', back_populates='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Destination(db.Model):
    __tablename__ = 'destinations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    country = db.Column(db.String(100), default='India', nullable=False)
    region = db.Column(db.String(100), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # Hill Station, Beach, Heritage, Nature
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    estimated_budget = db.Column(db.Numeric(10, 2), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    attractions = db.relationship('Attraction', back_populates='destination', cascade='all, delete-orphan', lazy='joined')
    packages = db.relationship('Package', back_populates='destination', cascade='all, delete-orphan', lazy='dynamic')
    hotels = db.relationship('Hotel', back_populates='destination', cascade='all, delete-orphan', lazy='dynamic')
    reviews = db.relationship('Review', back_populates='destination', cascade='all, delete-orphan', lazy='dynamic')
    favourites = db.relationship('Favourite', back_populates='destination', cascade='all, delete-orphan', lazy='dynamic')

    @property
    def average_rating(self):
        revs = [r.rating for r in self.reviews if r.rating is not None]
        return round(sum(revs) / len(revs), 1) if revs else 4.8

    @property
    def review_count(self):
        return self.reviews.count()

    def __repr__(self):
        return f'<Destination {self.name}>'


class Attraction(db.Model):
    __tablename__ = 'attractions'

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    entry_fee = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    opening_information = db.Column(db.String(200), nullable=True)

    destination = db.relationship('Destination', back_populates='attractions')

    def __repr__(self):
        return f'<Attraction {self.name}>'


class Package(db.Model):
    __tablename__ = 'packages'

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    price_per_person = db.Column(db.Numeric(10, 2), nullable=False)
    inclusions = db.Column(db.Text, nullable=False)  # Comma or newline separated
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    destination = db.relationship('Destination', back_populates='packages')
    itineraries = db.relationship('PackageItinerary', back_populates='package', cascade='all, delete-orphan', order_by='PackageItinerary.day_number')
    bookings = db.relationship('Booking', back_populates='package', lazy='dynamic')

    @property
    def inclusion_list(self):
        if not self.inclusions:
            return []
        return [inc.strip() for inc in self.inclusions.replace('\n', ',').split(',') if inc.strip()]

    def __repr__(self):
        return f'<Package {self.name}>'


class PackageItinerary(db.Model):
    __tablename__ = 'package_itineraries'

    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id', ondelete='CASCADE'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    package = db.relationship('Package', back_populates='itineraries')

    def __repr__(self):
        return f'<Itinerary Day {self.day_number}: {self.title}>'


class Hotel(db.Model):
    __tablename__ = 'hotels'

    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(150), nullable=False, index=True)
    address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    amenities = db.Column(db.Text, nullable=False)  # Comma separated
    rating = db.Column(db.Numeric(3, 2), default=4.5, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    destination = db.relationship('Destination', back_populates='hotels')
    rooms = db.relationship('Room', back_populates='hotel', cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='hotel', lazy='dynamic')

    @property
    def amenity_list(self):
        if not self.amenities:
            return []
        return [a.strip() for a in self.amenities.split(',') if a.strip()]

    def __repr__(self):
        return f'<Hotel {self.name}>'


class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id', ondelete='CASCADE'), nullable=False)
    room_type = db.Column(db.String(100), nullable=False)  # e.g., Deluxe King, Mountain View Suite
    capacity = db.Column(db.Integer, default=2, nullable=False)
    price_per_night = db.Column(db.Numeric(10, 2), nullable=False)
    total_rooms = db.Column(db.Integer, default=5, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    hotel = db.relationship('Hotel', back_populates='rooms')
    bookings = db.relationship('Booking', back_populates='room', lazy='dynamic')
    reservations = db.relationship('RoomReservation', back_populates='room', cascade='all, delete-orphan', lazy='dynamic')

    def __repr__(self):
        return f'<Room {self.room_type} at {self.hotel.name if self.hotel else self.hotel_id}>'


class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    booking_reference = db.Column(db.String(30), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='RESTRICT'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('packages.id', ondelete='SET NULL'), nullable=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='SET NULL'), nullable=True)
    check_in = db.Column(db.Date, nullable=False)
    check_out = db.Column(db.Date, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    booking_status = db.Column(db.String(20), default='PENDING', nullable=False)  # PENDING, CONFIRMED, CANCELLED, COMPLETED
    special_requests = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='bookings')
    package = db.relationship('Package', back_populates='bookings')
    room = db.relationship('Room', back_populates='bookings')
    payment = db.relationship('Payment', back_populates='booking', uselist=False, cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='booking', lazy='dynamic')
    status_history = db.relationship('BookingStatusHistory', back_populates='booking', cascade='all, delete-orphan', order_by='BookingStatusHistory.changed_at.desc()')
    reservations = db.relationship('RoomReservation', back_populates='booking', cascade='all, delete-orphan')

    @property
    def nights_count(self):
        if self.check_in and self.check_out:
            return (self.check_out - self.check_in).days
        return 0

    def __repr__(self):
        return f'<Booking {self.booking_reference} ({self.booking_status})>'


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # 'Pay at Property', 'UPI Demo', 'Card Demo'
    transaction_reference = db.Column(db.String(60), unique=True, nullable=False, index=True)
    payment_status = db.Column(db.String(20), default='PENDING', nullable=False)  # PENDING, SUCCESS, FAILED
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    booking = db.relationship('Booking', back_populates='payment')

    def __repr__(self):
        return f'<Payment {self.transaction_reference} - {self.payment_status}>'


class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id', ondelete='SET NULL'), nullable=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotels.id', ondelete='SET NULL'), nullable=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='SET NULL'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1 to 5
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='reviews')
    destination = db.relationship('Destination', back_populates='reviews')
    hotel = db.relationship('Hotel', back_populates='reviews')
    booking = db.relationship('Booking', back_populates='reviews')

    def __repr__(self):
        return f'<Review by User {self.user_id} - Rating {self.rating}>'


class Favourite(db.Model):
    __tablename__ = 'favourites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'destination_id', name='uq_user_destination_favourite'),
    )

    user = db.relationship('User', back_populates='favourites')
    destination = db.relationship('Destination', back_populates='favourites')

    def __repr__(self):
        return f'<Favourite User {self.user_id} Destination {self.destination_id}>'


class BookingStatusHistory(db.Model):
    __tablename__ = 'booking_status_history'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    old_status = db.Column(db.String(20), nullable=True)
    new_status = db.Column(db.String(20), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    changed_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    remarks = db.Column(db.Text, nullable=True)

    booking = db.relationship('Booking', back_populates='status_history')
    changer = db.relationship('User', foreign_keys=[changed_by])

    def __repr__(self):
        return f'<BookingStatusHistory {self.old_status} -> {self.new_status}>'


class RoomReservation(db.Model):
    """
    Inventory allocation table to safely prevent room overbooking
    across distinct dates and concurrent transactions.
    """
    __tablename__ = 'room_reservations'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id', ondelete='CASCADE'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id', ondelete='CASCADE'), nullable=False)
    reservation_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), default='ACTIVE', nullable=False)  # ACTIVE, RELEASED
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    booking = db.relationship('Booking', back_populates='reservations')
    room = db.relationship('Room', back_populates='reservations')

    def __repr__(self):
        return f'<RoomReservation Room {self.room_id} on {self.reservation_date} ({self.status})>'
