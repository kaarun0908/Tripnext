from datetime import datetime, date
from decimal import Decimal
from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.bookings import bookings_bp
from app.extensions import db
from app.models import Package, Room, Booking, Payment, Hotel
from app.forms import PackageBookingForm, HotelBookingForm, PaymentForm
from app.services.booking_service import (
    create_package_booking, create_hotel_booking,
    cancel_booking, check_room_availability
)
from app.services.payment_service import process_simulated_payment

@bookings_bp.route('/package/<int:package_id>', methods=['GET', 'POST'])
@login_required
def book_package(package_id):
    package = Package.query.get_or_404(package_id)
    if not package.is_active:
        flash('This package is currently not available for new reservations.', 'warning')
        return redirect(url_for('main.packages'))

    form = PackageBookingForm()
    if form.validate_on_submit():
        try:
            booking = create_package_booking(
                user_id=current_user.id,
                package_id=package.id,
                travel_date=form.check_in.data,
                number_of_guests=form.number_of_guests.data,
                special_requests=form.special_requests.data
            )
            flash(f'Package reservation created! Booking Reference: {booking.booking_reference}', 'success')
            return redirect(url_for('bookings.checkout', booking_id=booking.id))
        except Exception as e:
            flash(f'Unable to create booking: {str(e)}', 'danger')

    return render_template('package_booking.html', package=package, form=form)

@bookings_bp.route('/room/<int:room_id>', methods=['GET', 'POST'])
@login_required
def book_room(room_id):
    room = Room.query.get_or_404(room_id)
    if not room.is_active or not room.hotel.is_active:
        flash('This room is currently not available for reservation.', 'warning')
        return redirect(url_for('main.hotels'))

    form = HotelBookingForm()
    if form.validate_on_submit():
        check_in = form.check_in.data
        check_out = form.check_out.data
        guests = form.number_of_guests.data

        # Double check capacity
        if guests > room.capacity:
            flash(f'Selected guest count ({guests}) exceeds maximum capacity of {room.capacity} for this room.', 'danger')
            return render_template('room_booking.html', room=room, form=form)

        try:
            booking = create_hotel_booking(
                user_id=current_user.id,
                room_id=room.id,
                check_in_date=check_in,
                check_out_date=check_out,
                number_of_guests=guests,
                special_requests=form.special_requests.data
            )
            flash(f'Room reserved! Booking Reference: {booking.booking_reference}. Please complete payment.', 'success')
            return redirect(url_for('bookings.checkout', booking_id=booking.id))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            flash(f'Reservation failed due to system error: {str(e)}', 'danger')

    return render_template('room_booking.html', room=room, form=form)

@bookings_bp.route('/checkout/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def checkout(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Security check: User can access only their own bookings (or admin)
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if booking.booking_status == 'CANCELLED':
        flash('This booking is cancelled and cannot be paid for.', 'warning')
        return redirect(url_for('bookings.booking_detail', booking_id=booking.id))

    if booking.payment and booking.payment.payment_status == 'SUCCESS':
        flash('This booking has already been successfully paid.', 'info')
        return redirect(url_for('bookings.payment_result', booking_id=booking.id))

    form = PaymentForm()
    if form.validate_on_submit():
        try:
            payment = process_simulated_payment(
                booking_id=booking.id,
                payment_method=form.payment_method.data,
                simulate_status=form.simulate_status.data,
                simulated_account=form.simulated_account.data
            )
            if payment.payment_status == 'SUCCESS':
                flash('Payment completed successfully! Your booking is confirmed.', 'success')
            else:
                flash('Simulated payment failed. You may retry or select another payment method.', 'danger')

            return redirect(url_for('bookings.payment_result', booking_id=booking.id))
        except Exception as e:
            flash(f'Payment processing error: {str(e)}', 'danger')

    return render_template('checkout.html', booking=booking, form=form)

@bookings_bp.route('/payment-result/<int:booking_id>')
@login_required
def payment_result(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('payment_result.html', booking=booking)

@bookings_bp.route('/my-bookings')
@login_required
def my_bookings():
    status_filter = request.args.get('status')
    query = Booking.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter_by(booking_status=status_filter.upper())

    user_bookings = query.order_by(Booking.created_at.desc()).all()
    return render_template('my_bookings.html', bookings=user_bookings, current_filter=status_filter)

@bookings_bp.route('/<int:booking_id>')
@login_required
def booking_detail(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    return render_template('booking_detail.html', booking=booking)

@bookings_bp.route('/<int:booking_id>/cancel', methods=['POST'])
@login_required
def cancel(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id and not current_user.is_admin:
        abort(403)

    if booking.booking_status == 'CANCELLED':
        flash('This booking is already cancelled.', 'info')
        return redirect(url_for('bookings.booking_detail', booking_id=booking.id))

    try:
        cancel_booking(booking_id=booking.id, user_id=current_user.id, remarks='Cancelled by customer request')
        flash(f'Booking {booking.booking_reference} has been cancelled. Any room inventory has been released.', 'success')
    except Exception as e:
        flash(f'Could not cancel booking: {str(e)}', 'danger')

    return redirect(url_for('bookings.booking_detail', booking_id=booking.id))

@bookings_bp.route('/check-availability')
def check_availability():
    room_id = request.args.get('room_id', type=int)
    check_in_str = request.args.get('check_in')
    check_out_str = request.args.get('check_out')

    if not room_id or not check_in_str or not check_out_str:
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        check_in = datetime.strptime(check_in_str, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out_str, '%Y-%m-%d').date()
        if check_out <= check_in:
            return jsonify({'available': False, 'message': 'Check-out date must follow check-in.'})

        is_avail, count = check_room_availability(room_id, check_in, check_out)
        return jsonify({
            'available': is_avail,
            'rooms_left': count,
            'message': f'{count} room(s) available for selected dates' if is_avail else 'Sold out for selected dates'
        })
    except Exception as e:
        return jsonify({'available': False, 'error': str(e)}), 400
