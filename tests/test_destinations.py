from app.models import Destination, Favourite, User

def test_destinations_listing(client, db_session):
    response = client.get('/destinations')
    assert response.status_code == 200
    assert b'Ooty Test' in response.data

def test_destination_search_filter(client, db_session):
    # Search for existing
    response = client.get('/destinations?search=Ooty')
    assert response.status_code == 200
    assert b'Ooty Test' in response.data

    # Search for non-existing
    response_none = client.get('/destinations?search=NonExistentCity123')
    assert response_none.status_code == 200
    assert b'No Destinations Found' in response_none.data

def test_destination_detail(client, db_session):
    dest = Destination.query.filter_by(name='Ooty Test').first()
    response = client.get(f'/destinations/{dest.id}')
    assert response.status_code == 200
    assert b'Ooty Test' in response.data
    assert b'About Ooty Test' in response.data

def test_favourite_toggle(auth_client, db_session):
    dest = Destination.query.filter_by(name='Ooty Test').first()
    user = User.query.filter_by(email='customer@test.com').first()

    # Toggle add
    res1 = auth_client.post(f'/favourites/toggle/{dest.id}', follow_redirects=True)
    assert res1.status_code == 200
    fav = Favourite.query.filter_by(user_id=user.id, destination_id=dest.id).first()
    assert fav is not None

    # Toggle remove
    res2 = auth_client.post(f'/favourites/toggle/{dest.id}', follow_redirects=True)
    assert res2.status_code == 200
    fav_after = Favourite.query.filter_by(user_id=user.id, destination_id=dest.id).first()
    assert fav_after is None
