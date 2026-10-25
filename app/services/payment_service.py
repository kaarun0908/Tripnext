import uuid
from datetime import datetime
from app.extensions import db
from app.models import Payment, Booking, BookingStatusHistory

def process_simulated_payment(booking_id, payment_method, simulate_status='SUCCESS', simulated_account=None):
    """
    Simulates a payment transaction cleanly and safely.
    Prevents duplicate payment records and updates booking status accordingly.
    """
    try:
        booking = Booking.query.get(booking_id)
        if not booking:
            raise ValueError("Booking not found.")

        # Check if already successfully paid
        if booking.payment and booking.payment.payment_status == 'SUCCESS':
            raise ValueError("This booking has already been successfully paid.")

        # Generate unique transaction reference
        tx_ref = f"TXN-{payment_method.replace(' ', '').upper()}-{uuid.uuid4().hex[:10].upper()}"

        payment = booking.payment
        if not payment:
            payment = Payment(
                booking_id=booking.id,
                amount=booking.total_amount,
                payment_method=payment_method,
                transaction_reference=tx_ref,
                payment_status=simulate_status
            )
            db.session.add(payment)
        else:
            payment.payment_method = payment_method
            payment.transaction_reference = tx_ref
            payment.payment_status = simulate_status
            payment.created_at = datetime.utcnow()

        # Update booking status
        old_status = booking.booking_status
        if simulate_status == 'SUCCESS':
            booking.booking_status = 'CONFIRMED'
            remarks = f"Simulated payment succeeded via {payment_method} ({tx_ref})"
        else:
            booking.booking_status = 'PENDING'
            remarks = f"Simulated payment failed via {payment_method} ({tx_ref})"

        history = BookingStatusHistory(
            booking_id=booking.id,
            old_status=old_status,
            new_status=booking.booking_status,
            changed_by=booking.user_id,
            remarks=remarks
        )
        db.session.add(history)

        db.session.commit()
        return payment

    except Exception:
        db.session.rollback()
        raise
