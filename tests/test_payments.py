from datetime import date, timedelta
from app.models import User, Package, Booking, Payment
from app.services.booking_service import create_package_booking
from app.services.payment_service import process_simulated_payment

def test_simulated_payment_success(db_session):
    user = User.query.filter_by(email='customer@test.com').first()
    pkg = Package.query.filter_by(name='Ooty Heritage Tour').first()
    booking = create_package_booking(user.id, pkg.id, date.today() + timedelta(days=5), 1)

    assert booking.booking_status == 'PENDING'

    payment = process_simulated_payment(
        booking_id=booking.id,
        payment_method='UPI Demo',
        simulate_status='SUCCESS',
        simulated_account='demo@upi'
    )

    assert payment.id is not None
    assert payment.payment_status == 'SUCCESS'
    assert payment.amount == booking.total_amount
    assert booking.booking_status == 'CONFIRMED'
    assert len(booking.status_history) >= 2

def test_simulated_payment_failure(db_session):
    user = User.query.filter_by(email='customer@test.com').first()
    pkg = Package.query.filter_by(name='Ooty Heritage Tour').first()
    booking = create_package_booking(user.id, pkg.id, date.today() + timedelta(days=6), 1)

    payment = process_simulated_payment(
        booking_id=booking.id,
        payment_method='Card Demo',
        simulate_status='FAILED'
    )

    assert payment.payment_status == 'FAILED'
    assert booking.booking_status == 'PENDING'

def test_duplicate_payment_prevention(db_session):
    user = User.query.filter_by(email='customer@test.com').first()
    pkg = Package.query.filter_by(name='Ooty Heritage Tour').first()
    booking = create_package_booking(user.id, pkg.id, date.today() + timedelta(days=7), 1)

    # First payment succeeds
    process_simulated_payment(booking.id, 'UPI Demo', 'SUCCESS')

    # Attempting second payment must raise ValueError
    try:
        process_simulated_payment(booking.id, 'Card Demo', 'SUCCESS')
        assert False, "Expected ValueError on duplicate payment"
    except ValueError as e:
        assert "already been successfully paid" in str(e)
