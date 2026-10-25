from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, BooleanField,
    TextAreaField, DecimalField, IntegerField, SelectField, DateField
)
from wtforms.validators import (
    DataRequired, Email, EqualTo, Length, Optional,
    NumberRange, ValidationError
)
from datetime import date
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    phone = StringField('Phone Number', validators=[Optional(), Length(min=7, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, message='Password must be at least 6 characters')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Create Account')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower().strip()).first():
            raise ValidationError('An account with this email address already exists.')

class PackageBookingForm(FlaskForm):
    check_in = DateField('Travel Start Date', validators=[DataRequired()])
    number_of_guests = IntegerField('Number of Travellers', validators=[DataRequired(), NumberRange(min=1, max=50, message='Must be between 1 and 50 travellers')])
    special_requests = TextAreaField('Special Requests / Dietary Requirements', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Proceed to Payment')

    def validate_check_in(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Travel date cannot be in the past.')

class HotelBookingForm(FlaskForm):
    check_in = DateField('Check-in Date', validators=[DataRequired()])
    check_out = DateField('Check-out Date', validators=[DataRequired()])
    number_of_guests = IntegerField('Number of Guests', validators=[DataRequired(), NumberRange(min=1, max=10, message='Must be between 1 and 10 guests per room')])
    special_requests = TextAreaField('Special Requests', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Reserve Room & Pay')

    def validate_check_in(self, field):
        if field.data and field.data < date.today():
            raise ValidationError('Check-in date cannot be in the past.')

    def validate_check_out(self, field):
        if self.check_in.data and field.data:
            if field.data <= self.check_in.data:
                raise ValidationError('Check-out date must be at least one day after check-in.')

class PaymentForm(FlaskForm):
    payment_method = SelectField(
        'Payment Method',
        choices=[
            ('UPI Demo', 'UPI (Google Pay / PhonePe / Paytm Demo)'),
            ('Card Demo', 'Credit / Debit Card (Demo)'),
            ('Pay at Property', 'Pay at Property / Cash on Arrival (Demo)')
        ],
        validators=[DataRequired()]
    )
    simulated_account = StringField('Demo UPI ID or Demo Card (Optional for Simulation)', validators=[Optional()])
    simulate_status = SelectField(
        'Simulation Result',
        choices=[
            ('SUCCESS', 'Simulate Successful Payment'),
            ('FAILED', 'Simulate Failed Payment')
        ],
        default='SUCCESS'
    )
    submit = SubmitField('Authorize Demo Payment')

class ReviewForm(FlaskForm):
    rating = SelectField(
        'Rating',
        choices=[('5', '5 - Excellent'), ('4', '4 - Very Good'), ('3', '3 - Average'), ('2', '2 - Poor'), ('1', '1 - Terrible')],
        validators=[DataRequired()]
    )
    comment = TextAreaField('Your Review', validators=[DataRequired(), Length(min=10, max=1000, message='Review must be between 10 and 1000 characters.')])
    submit = SubmitField('Submit Review')

class DestinationFilterForm(FlaskForm):
    search = StringField('Search Destination or Region', validators=[Optional()])
    category = SelectField(
        'Category',
        choices=[('', 'All Categories'), ('Hill Station', 'Hill Station'), ('Beach', 'Beach'), ('Heritage', 'Heritage'), ('Nature', 'Nature & Wildlife'), ('Backwaters', 'Backwaters')],
        validators=[Optional()]
    )
    sort_by = SelectField(
        'Sort By',
        choices=[('name_asc', 'Name (A - Z)'), ('name_desc', 'Name (Z - A)'), ('price_asc', 'Budget: Low to High'), ('price_desc', 'Budget: High to Low'), ('popular', 'Most Popular')],
        default='popular',
        validators=[Optional()]
    )
    submit = SubmitField('Filter')

# Administrator forms
class AdminDestinationForm(FlaskForm):
    name = StringField('Destination Name', validators=[DataRequired(), Length(max=100)])
    country = StringField('Country', default='India', validators=[DataRequired(), Length(max=100)])
    region = StringField('State / Region', validators=[DataRequired(), Length(max=100)])
    category = SelectField(
        'Category',
        choices=[('Hill Station', 'Hill Station'), ('Beach', 'Beach'), ('Heritage', 'Heritage'), ('Nature', 'Nature & Wildlife'), ('Backwaters', 'Backwaters')],
        validators=[DataRequired()]
    )
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = StringField('Hero Image URL', validators=[DataRequired(), Length(max=500)])
    estimated_budget = DecimalField('Estimated Budget (INR)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    is_active = BooleanField('Active & Published', default=True)
    submit = SubmitField('Save Destination')

class AdminPackageForm(FlaskForm):
    destination_id = SelectField('Destination', coerce=int, validators=[DataRequired()])
    name = StringField('Package Name', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('Description', validators=[DataRequired()])
    duration_days = IntegerField('Duration (Days)', validators=[DataRequired(), NumberRange(min=1, max=30)])
    price_per_person = DecimalField('Price per Person (INR)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    inclusions = TextAreaField('Inclusions (Comma separated, e.g. Hotels, Breakfast, Sightseeing)', validators=[DataRequired()])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=500)])
    is_active = BooleanField('Active & Available', default=True)
    submit = SubmitField('Save Package')

class AdminHotelForm(FlaskForm):
    destination_id = SelectField('Destination', coerce=int, validators=[DataRequired()])
    name = StringField('Hotel Name', validators=[DataRequired(), Length(max=150)])
    address = StringField('Address / Area', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[DataRequired()])
    amenities = TextAreaField('Amenities (Comma separated: WiFi, Pool, Spa, Dining)', validators=[DataRequired()])
    rating = DecimalField('Rating (0 - 5.0)', places=1, default=4.5, validators=[DataRequired(), NumberRange(min=1, max=5)])
    image_url = StringField('Image URL', validators=[Optional(), Length(max=500)])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Hotel')

class AdminRoomForm(FlaskForm):
    hotel_id = SelectField('Hotel', coerce=int, validators=[DataRequired()])
    room_type = StringField('Room Type (e.g. Deluxe Suite)', validators=[DataRequired(), Length(max=100)])
    capacity = IntegerField('Max Capacity (Guests)', default=2, validators=[DataRequired(), NumberRange(min=1, max=10)])
    price_per_night = DecimalField('Price per Night (INR)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    total_rooms = IntegerField('Total Room Inventory', default=5, validators=[DataRequired(), NumberRange(min=1, max=100)])
    is_active = BooleanField('Available for Booking', default=True)
    submit = SubmitField('Save Room')
