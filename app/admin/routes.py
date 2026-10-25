from flask import render_template, redirect, url_for, flash, request, Response, abort
from flask_login import login_required, current_user
from app.admin import admin_bp
from app.extensions import db
from app.decorators import admin_required
from app.models import (
    User, Destination, Attraction, Package, PackageItinerary,
    Hotel, Room, Booking, Payment, Review
)
from app.forms import (
    AdminDestinationForm, AdminPackageForm,
    AdminHotelForm, AdminRoomForm
)
from app.services.report_service import (
    get_admin_dashboard_metrics, get_chart_data, generate_bookings_csv
)
from app.services.booking_service import update_booking_status

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    metrics = get_admin_dashboard_metrics()
    chart_data = get_chart_data()
    return render_template('admin/dashboard.html', metrics=metrics, chart_data=chart_data)

# ==================== DESTINATIONS ====================
@admin_bp.route('/destinations')
@login_required
@admin_required
def destinations():
    all_dests = Destination.query.order_by(Destination.name.asc()).all()
    return render_template('admin/destinations.html', destinations=all_dests)

@admin_bp.route('/destinations/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_destination():
    form = AdminDestinationForm()
    if form.validate_on_submit():
        dest = Destination(
            name=form.name.data.strip(),
            country=form.country.data.strip(),
            region=form.region.data.strip(),
            category=form.category.data,
            description=form.description.data.strip(),
            image_url=form.image_url.data.strip(),
            estimated_budget=form.estimated_budget.data,
            is_active=form.is_active.data
        )
        db.session.add(dest)
        db.session.commit()
        flash(f'Destination "{dest.name}" created successfully.', 'success')
        return redirect(url_for('admin.destinations'))

    return render_template('admin/destination_form.html', form=form, title='Add New Destination')

@admin_bp.route('/destinations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_destination(id):
    dest = Destination.query.get_or_404(id)
    form = AdminDestinationForm(obj=dest)
    if form.validate_on_submit():
        form.populate_obj(dest)
        db.session.commit()
        flash(f'Destination "{dest.name}" updated successfully.', 'success')
        return redirect(url_for('admin.destinations'))

    return render_template('admin/destination_form.html', form=form, destination=dest, title='Edit Destination')

@admin_bp.route('/destinations/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_destination(id):
    dest = Destination.query.get_or_404(id)
    name = dest.name
    # Soft delete / deactivation if it has active bookings or packages
    dest.is_active = False
    db.session.commit()
    flash(f'Destination "{name}" has been deactivated.', 'info')
    return redirect(url_for('admin.destinations'))

# ==================== PACKAGES ====================
@admin_bp.route('/packages')
@login_required
@admin_required
def packages():
    all_packages = Package.query.order_by(Package.id.desc()).all()
    return render_template('admin/packages.html', packages=all_packages)

@admin_bp.route('/packages/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_package():
    form = AdminPackageForm()
    form.destination_id.choices = [(d.id, f"{d.name} ({d.region})") for d in Destination.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        pkg = Package(
            destination_id=form.destination_id.data,
            name=form.name.data.strip(),
            description=form.description.data.strip(),
            duration_days=form.duration_days.data,
            price_per_person=form.price_per_person.data,
            inclusions=form.inclusions.data.strip(),
            image_url=form.image_url.data.strip() if form.image_url.data else None,
            is_active=form.is_active.data
        )
        db.session.add(pkg)
        db.session.commit()
        flash(f'Package "{pkg.name}" created successfully.', 'success')
        return redirect(url_for('admin.packages'))

    return render_template('admin/package_form.html', form=form, title='Add Travel Package')

@admin_bp.route('/packages/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_package(id):
    pkg = Package.query.get_or_404(id)
    form = AdminPackageForm(obj=pkg)
    form.destination_id.choices = [(d.id, f"{d.name} ({d.region})") for d in Destination.query.all()]

    if form.validate_on_submit():
        form.populate_obj(pkg)
        db.session.commit()
        flash(f'Package "{pkg.name}" updated successfully.', 'success')
        return redirect(url_for('admin.packages'))

    return render_template('admin/package_form.html', form=form, package=pkg, title='Edit Travel Package')

@admin_bp.route('/packages/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_package(id):
    pkg = Package.query.get_or_404(id)
    pkg.is_active = False
    db.session.commit()
    flash(f'Package "{pkg.name}" deactivated.', 'info')
    return redirect(url_for('admin.packages'))

# ==================== HOTELS & ROOMS ====================
@admin_bp.route('/hotels')
@login_required
@admin_required
def hotels():
    all_hotels = Hotel.query.order_by(Hotel.id.desc()).all()
    return render_template('admin/hotels.html', hotels=all_hotels)

@admin_bp.route('/hotels/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_hotel():
    form = AdminHotelForm()
    form.destination_id.choices = [(d.id, d.name) for d in Destination.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        h = Hotel(
            destination_id=form.destination_id.data,
            name=form.name.data.strip(),
            address=form.address.data.strip(),
            description=form.description.data.strip(),
            amenities=form.amenities.data.strip(),
            rating=form.rating.data,
            image_url=form.image_url.data.strip() if form.image_url.data else None,
            is_active=form.is_active.data
        )
        db.session.add(h)
        db.session.commit()
        flash(f'Hotel "{h.name}" created successfully.', 'success')
        return redirect(url_for('admin.hotels'))

    return render_template('admin/hotel_form.html', form=form, title='Add Hotel')

@admin_bp.route('/hotels/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_hotel(id):
    hotel = Hotel.query.get_or_404(id)
    form = AdminHotelForm(obj=hotel)
    form.destination_id.choices = [(d.id, d.name) for d in Destination.query.all()]

    if form.validate_on_submit():
        form.populate_obj(hotel)
        db.session.commit()
        flash(f'Hotel "{hotel.name}" updated successfully.', 'success')
        return redirect(url_for('admin.hotels'))

    return render_template('admin/hotel_form.html', form=form, hotel=hotel, title='Edit Hotel')

@admin_bp.route('/rooms')
@login_required
@admin_required
def rooms():
    all_rooms = Room.query.order_by(Room.id.desc()).all()
    return render_template('admin/rooms.html', rooms=all_rooms)

@admin_bp.route('/rooms/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_room():
    form = AdminRoomForm()
    form.hotel_id.choices = [(h.id, f"{h.name} ({h.destination.name})") for h in Hotel.query.filter_by(is_active=True).all()]

    if form.validate_on_submit():
        room = Room(
            hotel_id=form.hotel_id.data,
            room_type=form.room_type.data.strip(),
            capacity=form.capacity.data,
            price_per_night=form.price_per_night.data,
            total_rooms=form.total_rooms.data,
            is_active=form.is_active.data
        )
        db.session.add(room)
        db.session.commit()
        flash(f'Room "{room.room_type}" added to hotel.', 'success')
        return redirect(url_for('admin.rooms'))

    return render_template('admin/room_form.html', form=form, title='Add Hotel Room')

@admin_bp.route('/rooms/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_room(id):
    room = Room.query.get_or_404(id)
    form = AdminRoomForm(obj=room)
    form.hotel_id.choices = [(h.id, f"{h.name} ({h.destination.name})") for h in Hotel.query.all()]

    if form.validate_on_submit():
        form.populate_obj(room)
        db.session.commit()
        flash(f'Room "{room.room_type}" updated successfully.', 'success')
        return redirect(url_for('admin.rooms'))

    return render_template('admin/room_form.html', form=form, room=room, title='Edit Room')

# ==================== BOOKINGS MANAGEMENT ====================
@admin_bp.route('/bookings')
@login_required
@admin_required
def bookings():
    status = request.args.get('status')
    query = Booking.query
    if status:
        query = query.filter_by(booking_status=status.upper())
    all_bookings = query.order_by(Booking.created_at.desc()).all()
    return render_template('admin/bookings.html', bookings=all_bookings, current_status=status)

@admin_bp.route('/bookings/<int:id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_status(id):
    new_status = request.form.get('status')
    remarks = request.form.get('remarks', 'Updated by Administrator')
    if new_status in ['PENDING', 'CONFIRMED', 'CANCELLED', 'COMPLETED']:
        update_booking_status(booking_id=id, new_status=new_status, changed_by=current_user.id, remarks=remarks)
        flash(f'Booking #{id} updated to {new_status}.', 'success')
    else:
        flash('Invalid status provided.', 'danger')
    return redirect(url_for('admin.bookings'))

# ==================== USERS & REVIEWS ====================
@admin_bp.route('/users')
@login_required
@admin_required
def users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=all_users)

@admin_bp.route('/users/<int:id>/toggle-role', methods=['POST'])
@login_required
@admin_required
def toggle_user_role(id):
    user = User.query.get_or_404(id)
    if user.id == current_user.id:
        flash('You cannot alter your own administrator role.', 'warning')
        return redirect(url_for('admin.users'))

    user.role = 'customer' if user.role == 'admin' else 'admin'
    db.session.commit()
    flash(f'User "{user.full_name}" role changed to {user.role}.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/reviews')
@login_required
@admin_required
def reviews():
    all_reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template('admin/reviews.html', reviews=all_reviews)

@admin_bp.route('/reviews/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_review(id):
    review = Review.query.get_or_404(id)
    db.session.delete(review)
    db.session.commit()
    flash('Review deleted by moderator.', 'info')
    return redirect(url_for('admin.reviews'))

# ==================== REPORTS & EXPORT ====================
@admin_bp.route('/reports')
@login_required
@admin_required
def reports():
    metrics = get_admin_dashboard_metrics()
    chart_data = get_chart_data()
    return render_template('admin/reports.html', metrics=metrics, chart_data=chart_data)

@admin_bp.route('/reports/export/bookings')
@login_required
@admin_required
def export_bookings_csv():
    csv_data = generate_bookings_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=tripnest_bookings_report.csv"}
    )
