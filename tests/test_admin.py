from app.models import Destination, Booking, User
from decimal import Decimal

def test_admin_access_allowed(admin_client, db_session):
    response = admin_client.get('/admin/')
    assert response.status_code == 200
    assert b'TripNest Analytics &amp; Operations Center' in response.data or b'TripNest Analytics & Operations Center' in response.data

def test_customer_access_forbidden(auth_client, db_session):
    # Customer user attempts to open /admin/
    response = auth_client.get('/admin/')
    assert response.status_code == 403

def test_admin_add_destination(admin_client, db_session):
    response = admin_client.post('/admin/destinations/new', data={
        'name': 'Jaipur Royal',
        'country': 'India',
        'region': 'Rajasthan',
        'category': 'Heritage',
        'description': 'The Pink City of India with magnificent palaces and forts.',
        'image_url': 'https://example.com/jaipur.jpg',
        'estimated_budget': '18000.00',
        'is_active': 'y'
    }, follow_redirects=True)

    assert response.status_code == 200
    d = Destination.query.filter_by(name='Jaipur Royal').first()
    assert d is not None
    assert d.category == 'Heritage'
    assert d.estimated_budget == Decimal('18000.00')

def test_admin_export_bookings_csv(admin_client, db_session):
    response = admin_client.get('/admin/reports/export/bookings')
    assert response.status_code == 200
    assert response.mimetype == 'text/csv'
    assert b'Booking Reference,Customer Name' in response.data
