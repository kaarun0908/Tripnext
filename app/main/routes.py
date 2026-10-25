from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user, login_required
from sqlalchemy import or_, desc, asc
from app.main import main_bp
from app.extensions import db
from app.models import (
    Destination, Package, Hotel, Room, Review, Favourite, Booking
)
from app.forms import DestinationFilterForm, ReviewForm

@main_bp.route('/')
def index():
    popular_destinations = Destination.query.filter_by(is_active=True).limit(6).all()
    featured_packages = Package.query.filter_by(is_active=True).limit(4).all()
    recommended_hotels = Hotel.query.filter_by(is_active=True).limit(4).all()
    recent_reviews = Review.query.order_by(Review.created_at.desc()).limit(3).all()
    
    return render_template(
        'index.html',
        popular_destinations=popular_destinations,
        featured_packages=featured_packages,
        recommended_hotels=recommended_hotels,
        recent_reviews=recent_reviews
    )

@main_bp.route('/destinations')
def destinations():
    form = DestinationFilterForm(request.args)
    query = Destination.query.filter_by(is_active=True)

    # Search keyword
    search = request.args.get('search', '').strip()
    if search:
        search_filter = or_(
            Destination.name.ilike(f'%{search}%'),
            Destination.region.ilike(f'%{search}%'),
            Destination.category.ilike(f'%{search}%'),
            Destination.description.ilike(f'%{search}%')
        )
        query = query.filter(search_filter)

    # Category filter
    category = request.args.get('category', '').strip()
    if category:
        query = query.filter(Destination.category == category)

    # Sorting
    sort_by = request.args.get('sort_by', 'popular')
    if sort_by == 'name_asc':
        query = query.order_by(asc(Destination.name))
    elif sort_by == 'name_desc':
        query = query.order_by(desc(Destination.name))
    elif sort_by == 'price_asc':
        query = query.order_by(asc(Destination.estimated_budget))
    elif sort_by == 'price_desc':
        query = query.order_by(desc(Destination.estimated_budget))
    else:
        query = query.order_by(desc(Destination.id))

    all_destinations = query.all()

    # Get user favourite destination IDs for heart toggle
    user_fav_ids = set()
    if current_user.is_authenticated:
        favs = Favourite.query.filter_by(user_id=current_user.id).all()
        user_fav_ids = {f.destination_id for f in favs}

    return render_template(
        'destinations.html',
        destinations=all_destinations,
        form=form,
        user_fav_ids=user_fav_ids,
        search=search,
        selected_category=category,
        sort_by=sort_by
    )

@main_bp.route('/destinations/<int:destination_id>')
def destination_detail(destination_id):
    dest = Destination.query.get_or_404(destination_id)
    packages = Package.query.filter_by(destination_id=dest.id, is_active=True).all()
    hotels = Hotel.query.filter_by(destination_id=dest.id, is_active=True).all()
    reviews = Review.query.filter_by(destination_id=dest.id).order_by(Review.created_at.desc()).all()

    is_fav = False
    can_review = False
    if current_user.is_authenticated:
        is_fav = Favourite.query.filter_by(user_id=current_user.id, destination_id=dest.id).first() is not None
        # User is eligible to review if they have a completed/confirmed booking for this destination or its packages
        user_booking = Booking.query.filter(
            Booking.user_id == current_user.id,
            Booking.booking_status.in_(['CONFIRMED', 'COMPLETED'])
        ).first()
        existing_review = Review.query.filter_by(user_id=current_user.id, destination_id=dest.id).first()
        can_review = bool(user_booking) and (existing_review is None)

    review_form = ReviewForm()

    return render_template(
        'destination_detail.html',
        destination=dest,
        packages=packages,
        hotels=hotels,
        reviews=reviews,
        is_fav=is_fav,
        can_review=can_review,
        review_form=review_form
    )

@main_bp.route('/packages')
def packages():
    query = Package.query.filter_by(is_active=True)
    destination_id = request.args.get('destination_id', type=int)
    if destination_id:
        query = query.filter_by(destination_id=destination_id)

    all_packages = query.order_by(Package.price_per_person.asc()).all()
    all_destinations = Destination.query.filter_by(is_active=True).all()

    return render_template(
        'packages.html',
        packages=all_packages,
        destinations=all_destinations,
        selected_destination_id=destination_id
    )

@main_bp.route('/packages/<int:package_id>')
def package_detail(package_id):
    pkg = Package.query.get_or_404(package_id)
    return render_template('package_detail.html', package=pkg)

@main_bp.route('/hotels')
def hotels():
    query = Hotel.query.filter_by(is_active=True)
    destination_id = request.args.get('destination_id', type=int)
    if destination_id:
        query = query.filter_by(destination_id=destination_id)

    all_hotels = query.order_by(Hotel.rating.desc()).all()
    all_destinations = Destination.query.filter_by(is_active=True).all()

    return render_template(
        'hotels.html',
        hotels=all_hotels,
        destinations=all_destinations,
        selected_destination_id=destination_id
    )

@main_bp.route('/hotels/<int:hotel_id>')
def hotel_detail(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    rooms = Room.query.filter_by(hotel_id=hotel.id, is_active=True).all()
    reviews = Review.query.filter_by(hotel_id=hotel.id).order_by(Review.created_at.desc()).all()
    return render_template('hotel_detail.html', hotel=hotel, rooms=rooms, reviews=reviews)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    upcoming = [b for b in bookings if b.booking_status == 'CONFIRMED']
    pending = [b for b in bookings if b.booking_status == 'PENDING']
    cancelled = [b for b in bookings if b.booking_status == 'CANCELLED']
    completed = [b for b in bookings if b.booking_status == 'COMPLETED']
    favourites = Favourite.query.filter_by(user_id=current_user.id).all()
    user_reviews = Review.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'dashboard.html',
        upcoming=upcoming,
        pending=pending,
        cancelled=cancelled,
        completed=completed,
        favourites=favourites,
        reviews=user_reviews
    )

@main_bp.route('/favourites')
@login_required
def favourites():
    fav_items = Favourite.query.filter_by(user_id=current_user.id).order_by(Favourite.created_at.desc()).all()
    return render_template('favourites.html', favourites=fav_items)

@main_bp.route('/favourites/toggle/<int:destination_id>', methods=['POST'])
@login_required
def toggle_favourite(destination_id):
    dest = Destination.query.get_or_404(destination_id)
    fav = Favourite.query.filter_by(user_id=current_user.id, destination_id=dest.id).first()

    if fav:
        db.session.delete(fav)
        db.session.commit()
        saved = False
        message = f'Removed {dest.name} from your favourites.'
    else:
        new_fav = Favourite(user_id=current_user.id, destination_id=dest.id)
        db.session.add(new_fav)
        db.session.commit()
        saved = True
        message = f'Added {dest.name} to your favourites.'

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'success': True, 'saved': saved, 'message': message})

    flash(message, 'info')
    return redirect(request.referrer or url_for('main.destinations'))

@main_bp.route('/reviews/submit', methods=['POST'])
@login_required
def submit_review():
    form = ReviewForm()
    destination_id = request.form.get('destination_id', type=int)
    hotel_id = request.form.get('hotel_id', type=int)

    if form.validate_on_submit():
        # Check duplicate
        if destination_id:
            dup = Review.query.filter_by(user_id=current_user.id, destination_id=destination_id).first()
            if dup:
                flash('You have already submitted a review for this destination.', 'warning')
                return redirect(url_for('main.destination_detail', destination_id=destination_id))

        review = Review(
            user_id=current_user.id,
            destination_id=destination_id,
            hotel_id=hotel_id,
            rating=int(form.rating.data),
            comment=form.comment.data.strip()
        )
        db.session.add(review)
        db.session.commit()
        flash('Thank you! Your review has been submitted successfully.', 'success')

        if destination_id:
            return redirect(url_for('main.destination_detail', destination_id=destination_id))
        elif hotel_id:
            return redirect(url_for('main.hotel_detail', hotel_id=hotel_id))

    flash('Please provide valid review details.', 'danger')
    return redirect(url_for('main.index'))
