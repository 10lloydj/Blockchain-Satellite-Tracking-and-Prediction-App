import pytest
from flaskr.satellite import *
from datetime import datetime, date

# sets the fixture id to be the space station
@pytest.fixture
def set_satid():
    return 25544

@pytest.fixture
def set_satinfo(set_satid):
    return get_info(set_satid)

@pytest.fixture
def timestamp():
    return 1521354419

# tests that the users receive an error message without a satellite id entered
def test_index_validation_no_ID(client):
    # data passes the satelliteid 
    response = client.post('/satelliteindex', data={'satelliteid': ''})
    assert response.status_code == 200
    assert  b"Satellite ID is required" in response.data

def test_index_validation_invalid_ID(client):
    # data passes the satelliteid 
    response = client.post('/satelliteindex', data={'satelliteid': 'tehdhdh'})
    assert response.status_code == 200
    assert  b"Satellite ID is invalid" in response.data

# tests get_info functions returns a dictionary
def test_get_info(set_satid):
    info = get_info(set_satid)
    assert type(info) is dict

def test_check_sat_true(set_satid):
    info = get_info(set_satid)
    result = check_sat(info)
    assert result == True

def test_check_sat_false():
    info = get_info('tgffh')
    result = check_sat(info)
    assert result == False

# tests satToStr function to change satinfo to all string in a list (array)
def test_satToStr(set_satinfo):
    array = satToStr(set_satinfo)
    assert type(array) is list

# test getUTC function to string
def test_getUTC(timestamp):
    utc = getUTC(timestamp)
    assert type(utc) is str

#CURRENTLY CANT FIND THE CORRECT DATATYPE TO SHOW ITS A HASH

# test saveSat saves the satinfo and returns the hash 
#def test_saveSat(set_satinfo):
#    hash1 = saveSat(set_satinfo)
#    assert type(hash1) is object

def test_callSat():
    sat = callSat()
    assert type(sat) is list

def test_get_tle(set_satid):
    tle = get_tle(set_satid)
    assert type(tle) is str

def test_predlonglat1(set_satid):
    #####day = date.today().day
    ####month = date.today().month
    ###year = date.today().year
    ##now = datetime.now()
    #hour = now.hour

    lonlat = pred_longlat(get_tle(set_satid),1)
    assert type(lonlat) is tuple


# tests the all the prediction parameters for the different periods
def test_predlonglat2(set_satid):
    lonlat = pred_longlat(get_tle(set_satid),2)
    assert type(lonlat) is tuple
def test_predlonglat4(set_satid):
    lonlat = pred_longlat(get_tle(set_satid),4)
    assert type(lonlat) is tuple
def test_predlonglat6(set_satid):
    lonlat = pred_longlat(get_tle(set_satid),6)
    assert type(lonlat) is tuple
def test_predlonglat12(set_satid):
    lonlat = pred_longlat(get_tle(set_satid),12)
    assert type(lonlat) is tuple
def test_predlonglat24(set_satid):
    lonlat = pred_longlat(get_tle(set_satid),24)
    assert type(lonlat) is tuple
def test_predlonglat40(set_satid):
    lonlat = pred_longlat(get_tle(set_satid),40)
    assert type(lonlat) is tuple
def test_predlonglat70(set_satid):
    lonlat = pred_longlat(get_tle(set_satid),70)
    assert type(lonlat) is tuple


def test_period1():
    get = setPredtime(1)
    assert type(get) is tuple

def test_period2():
    get = setPredtime(2)
    assert type(get) is tuple
def test_period4():
    get = setPredtime(4)
    assert type(get) is tuple
def test_period6():
    get = setPredtime(6)
    assert type(get) is tuple
def test_period12():
    get = setPredtime(12)
    assert type(get) is tuple   
def test_period24():
    get = setPredtime(24)
    assert type(get) is tuple
def test_period40():
    get = setPredtime(40)
    assert type(get) is tuple
def test_period70():
    get = setPredtime(70)
    assert type(get) is tuple    