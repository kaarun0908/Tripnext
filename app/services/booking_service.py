import uuid
from datetime import timedelta, datetime, timezone
from decimal import Decimal
from sqlalchemy import func
from app.extensions import db
from app.models import (
    Booking, Room, Package, RoomReservation,
    BookingStatusHistory
)

def generate_booking_reference():
    """Generate a clean, professional booking reference like TN-2026-A1B2C3."""
    unique_suffix = uuid.uuid4().hex[:8].upper()
    return f"TN-{datetime.now(timezone.utc).year}-{unique_suffix}"

def check_room_availability(room_id, check_in_date, check_out_date):
    """
    Check if a room has at least 1 unit available for each night in the range.
    Returns (is_available: bool, min_available_count: int).
    """
    room = db.session.get(Room, room_id)
    if not room or not room.is_active or not room.hotel.is_active:
        return False, 0

    curr = check_in_date
    min_available = room.total_rooms

    while curr < check_out_date:
        # Count active reservations on curr date
        reserved_count = db.session.query(func.count(RoomReservation.id)).filter(
            RoomReservation.room_id == room_id,
            RoomReservation.reservation_date == curr,
            RoomReservation.status == 'ACTIVE'
        ).scalar() or 0

        available_today = room.total_rooms - reserved_count
        if available_today < min_available:
            min_available = available_today

        if available_today <= 0:
            return False, 0
        curr += timedelta(days=1)

    return True, max(0, min_available)

def create_hotel_booking(user_id, room_id, check_in_date, check_out_date, number_of_guests, special_requests=None):
    """
    Creates a hotel room booking safely inside a transaction.
    Allocates daily room reservations to guarantee no overbooking.
    """
    if check_out_date <= check_in_date:
        raise ValueError("Check-out date must be after check-in date.")

    try:
        room = db.session.get(Room, room_id)
        if not room or not room.is_active:
            raise ValueError("Room is no longer available.")

        if number_of_guests > room.capacity:
            raise ValueError(f"Number of guests ({number_of_guests}) exceeds room capacity ({room.capacity}).")

        # Verify availability day-by-day
        curr = check_in_date
        while curr < check_out_date:
            reserved = db.session.query(func.count(RoomReservation.id)).filter(
                RoomReservation.room_id == room_id,
                RoomReservation.reservation_date == curr,
                RoomReservation.status == 'ACTIVE'
            ).scalar() or 0

            if reserved >= room.total_rooms:
                raise ValueError(f"No rooms available for {curr.strftime('%b %d, %Y')}.")
            curr += timedelta(days=1)

        nights = (check_out_date - check_in_date).days
        total_amount = Decimal(str(room.price_per_night)) * Decimal(str(nights))

        booking = Booking(
            booking_reference=generate_booking_reference(),
            user_id=user_id,
            room_id=room.id,
            check_in=check_in_date,
            check_out=check_out_date,
            number_of_guests=number_of_guests,
            total_amount=total_amount,
            booking_status='PENDING',
            special_requests=special_requests
        )
        db.session.add(booking)
        db.session.flush()

        # Allocate daily inventory records
        curr = check_in_date
        while curr < check_out_date:
            res = RoomReservation(
                booking_id=booking.id,
                room_id=room.id,
                reservation_date=curr,
                status='ACTIVE'
            )
            db.session.add(res)
            curr += timedelta(days=1)

        # Audit status history
        history = BookingStatusHistory(
            booking_id=booking.id,
            old_status=None,
            new_status='PENDING',
            changed_by=user_id,
            remarks='Booking initiated by customer'
        )
        db.session.add(history)

        db.session.commit()
        return booking

    except Exception:
        db.session.rollback()
        raise

def create_package_booking(user_id, package_id, travel_date, number_of_guests, special_requests=None):
    """
    Creates a travel package booking with calculated end date.
    """
    try:
        package = db.session.get(Package, package_id)
        if not package or not package.is_active:
            raise ValueError("Travel package is not active or available.")

        if number_of_guests < 1:
            raise ValueError("Must have at least 1 traveller.")

        end_date = travel_date + timedelta(days=package.duration_days)
        total_amount = Decimal(str(package.price_per_person)) * Decimal(str(number_of_guests))

        booking = Booking(
            booking_reference=generate_booking_reference(),
            user_id=user_id,
            package_id=package.id,
            check_in=travel_date,
            check_out=end_date,
            number_of_guests=number_of_guests,
            total_amount=total_amount,
            booking_status='PENDING',
            special_requests=special_requests
        )
        db.session.add(booking)
        db.session.flush()

        history = BookingStatusHistory(
            booking_id=booking.id,
            old_status=None,
            new_status='PENDING',
            changed_by=user_id,
            remarks=f'Package booking initiated for {package.name}'
        )
        db.session.add(history)

        db.session.commit()
        return booking

    except Exception:
        db.session.rollback()
        raise

def cancel_booking(booking_id, user_id=None, remarks='Customer cancellation'):
    """
    Cancels a booking safely, releases any room inventory reservations,
    and logs status change history.
    """
    try:
        booking = db.session.get(Booking, booking_id)
        if not booking:
            raise ValueError("Booking not found.")

        if user_id and booking.user_id != user_id:
            raise PermissionError("Unauthorized to cancel this booking.")

        if booking.booking_status == 'CANCELLED':
            return booking

        old_status = booking.booking_status
        booking.booking_status = 'CANCELLED'

        # Release any room reservations
        RoomReservation.query.filter_by(booking_id=booking.id).update({'status': 'RELEASED'})

        if booking.payment and booking.payment.payment_status == 'PENDING':
            booking.payment.payment_status = 'FAILED'

        history = BookingStatusHistory(
            booking_id=booking.id,
            old_status=old_status,
            new_status='CANCELLED',
            changed_by=user_id or booking.user_id,
            remarks=remarks
        )
        db.session.add(history)

        db.session.commit()
        return booking

    except Exception:
        db.session.rollback()
        raise

def update_booking_status(booking_id, new_status, changed_by=None, remarks=None):
    """
    Administrative status updater for bookings.
    """
    try:
        booking = db.session.get(Booking, booking_id)
        if not booking:
            raise ValueError("Booking not found.")

        old_status = booking.booking_status
        booking.booking_status = new_status

        if new_status == 'CANCELLED':
            RoomReservation.query.filter_by(booking_id=booking.id).update({'status': 'RELEASED'})
        elif new_status == 'CONFIRMED' and booking.room_id:
            RoomReservation.query.filter_by(booking_id=booking.id).update({'status': 'ACTIVE'})

        history = BookingStatusHistory(
            booking_id=booking.id,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            remarks=remarks or f'Status updated to {new_status}'
        )
        db.session.add(history)
        db.session.commit()
        return booking

    except Exception:
        db.session.rollback()
        raise
