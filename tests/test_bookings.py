from datetime import date, timedelta
from decimal import Decimal
from app.models import (
    Package, Room, Booking, RoomReservation, User
)
from app.services.booking_service import (
    create_hotel_booking, create_package_booking,
    cancel_booking, check_room_availability
)

def test_package_booking_creation_and_pricing(db_session):
    user = User.query.filter_by(email='customer@test.com').first()
    pkg = Package.query.filter_by(name='Ooty Heritage Tour').first()

    travel_date = date.today() + timedelta(days=10)
    booking = create_package_booking(
        user_id=user.id,
        package_id=pkg.id,
        travel_date=travel_date,
        number_of_guests=3
    )

    assert booking.id is not None
    assert booking.booking_status == 'PENDING'
    # 3 travellers * 5000 = 15000
    assert booking.total_amount == Decimal('15000.00')
    assert booking.check_in == travel_date
    assert booking.check_out == travel_date + timedelta(days=pkg.duration_days)

def test_hotel_booking_and_room_reservations(db_session):
    user = User.query.filter_by(email='customer@test.com').first()
    room = Room.query.filter_by(room_type='Deluxe King').first()

    check_in = date.today() + timedelta(days=5)
    check_out = date.today() + timedelta(days=8)  # 3 nights

    booking = create_hotel_booking(
        user_id=user.id,
        room_id=room.id,
        check_in_date=check_in,
        check_out_date=check_out,
        number_of_guests=2
    )

    assert booking.id is not None
    # 3 nights * 3000 = 9000
    assert booking.total_amount == Decimal('9000.00')

    # Verify 3 daily RoomReservation rows created with status ACTIVE
    res_list = RoomReservation.query.filter_by(booking_id=booking.id, status='ACTIVE').all()
    assert len(res_list) == 3

def test_overbooking_prevention(db_session):
    """
    Room has total_rooms = 2.
    Creating 2 bookings for the same dates should succeed.
    A 3rd booking for the same dates MUST be blocked and raise ValueError!
    """
    user = User.query.filter_by(email='customer@test.com').first()
    room = Room.query.filter_by(room_type='Deluxe King').first()

    check_in = date.today() + timedelta(days=15)
    check_out = date.today() + timedelta(days=17)

    # Booking 1 (unit 1)
    b1 = create_hotel_booking(user.id, room.id, check_in, check_out, 2)
    assert b1.id is not None

    # Booking 2 (unit 2)
    b2 = create_hotel_booking(user.id, room.id, check_in, check_out, 2)
    assert b2.id is not None

    # Availability check should now show 0 rooms left
    avail, left = check_room_availability(room.id, check_in, check_out)
    assert avail is False
    assert left == 0

    # Booking 3 must fail due to inventory exhaustion
    try:
        create_hotel_booking(user.id, room.id, check_in, check_out, 2)
        assert False, "Expected ValueError for overbooking"
    except ValueError as e:
        assert "No rooms available" in str(e)

def test_booking_cancellation_and_inventory_release(db_session):
    user = User.query.filter_by(email='customer@test.com').first()
    room = Room.query.filter_by(room_type='Deluxe King').first()

    check_in = date.today() + timedelta(days=20)
    check_out = date.today() + timedelta(days=22)

    booking = create_hotel_booking(user.id, room.id, check_in, check_out, 2)
    assert booking.booking_status == 'PENDING'

    # Cancel booking
    cancel_booking(booking.id, user_id=user.id, remarks='Test Cancellation')

    updated = Booking.query.get(booking.id)
    assert updated.booking_status == 'CANCELLED'

    # Check that reservations are RELEASED
    reservations = RoomReservation.query.filter_by(booking_id=booking.id).all()
    for r in reservations:
        assert r.status == 'RELEASED'

    # Room is now available again for those dates
    avail, left = check_room_availability(room.id, check_in, check_out)
    assert avail is True
    assert left == room.total_rooms
