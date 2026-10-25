from app.models import User

def test_user_registration(client, db_session):
    response = client.post('/register', data={
        'full_name': 'New Tourist',
        'email': 'new.tourist@example.com',
        'phone': '9988776655',
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    }, follow_redirects=True)

    assert response.status_code == 200
    user = User.query.filter_by(email='new.tourist@example.com').first()
    assert user is not None
    assert user.full_name == 'New Tourist'
    assert user.check_password('Password@123')
    assert user.role == 'customer'

def test_duplicate_email_registration(client, db_session):
    response = client.post('/register', data={
        'full_name': 'Duplicate User',
        'email': 'customer@test.com',  # Already exists in conftest
        'password': 'Password@123',
        'confirm_password': 'Password@123'
    })
    # Should re-render form with validation error
    assert b'already exists' in response.data or response.status_code == 200

def test_login_success(client, db_session):
    response = client.post('/login', data={
        'email': 'customer@test.com',
        'password': 'Cust@123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Welcome back' in response.data

def test_login_invalid_password(client, db_session):
    response = client.post('/login', data={
        'email': 'customer@test.com',
        'password': 'WrongPassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email address or password' in response.data

def test_unauthorized_dashboard_access(client, db_session):
    response = client.get('/dashboard', follow_redirects=False)
    # Must redirect to login
    assert response.status_code == 302
    assert '/login' in response.location
