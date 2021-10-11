import pytest

def test_satindex(client):
    response = client.get('/satelliteindex')
    assert response.status_code == 200
    assert b"Satellite Tracker" in response.data

def test_about(client):
    response = client.get('/about')
    assert response.status_code == 200
    assert b"Satellite Tracker" in response.data

# tests the route is redirected correctly to track route
def test_satindex_to_track(client):
    # data passes the satelliteid 
    response = client.post('/satelliteindex', data={'satelliteid': 25544})
    assert response.status_code == 302
    assert 'http://localhost/track?satelliteid=25544' == response.headers['Location']

# test that the track route redirects to the block page
# this test runs the real smart contract, causing blocks to be created
def test_track_to_block(client):
    # lets flask know to call the save button and passes the comment from the front end
    response = client.post('/track?satelliteid=25544', data={'submit':'save', 'satComment': 'testthetest'})
    assert response.status_code == 302

def test_track_to_predict(client):
    # lets flask know to call the predict button
    response = client.post('/track?satelliteid=25544', data={'submit':'predict', 'predict': 6})
    assert response.status_code == 200