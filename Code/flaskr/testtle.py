import urllib.request, json
from datetime import datetime, date, timedelta
from pytz import timezone
from skyfield.api import load, EarthSatellite, wgs84


api_key = 'KQ9N7M-XWZL5A-NV4CAK-4NG8'

def get_tle(satid):
    #formats the tle into a json
    tlejson = "https://api.n2yo.com/rest/v1/satellite/tle/25544&apiKey={}".format(api_key)
    with urllib.request.urlopen(tlejson) as responsepos:
        data = json.loads(responsepos.read())
    tle = data['tle']
    return(tle)

def get_info(satelliteid):
    #formats the satellite id and the api key into the link
    positionurl = "https://api.n2yo.com/rest/v1/satellite/positions/{}/53.48095/-2.23743/38/1/&apiKey={}".format(satelliteid, api_key)

    # json data parsed into python dictionary
    with urllib.request.urlopen(positionurl) as responsepos:
        data = json.loads(responsepos.read())

    return data

def pred_longlat(tle):
    #time abstraction
    ts = load.timescale()
    time = ts.utc(2021, 5, 6, 11, 16, 25)
    # splits the TLE elements into their lines
    line1, line2 = tle.splitlines()
    # represents the tle data as the satellite
    satellite = EarthSatellite(line1, line2)
    #utc(year, month=1, day=1, hour=0, minute=0, second=0.0)
    #time = ts.utc(year, month, day, hour)
    # retrieves the correct timezone
    uk = timezone('Europe/London')

    dt = datetime.now()
    predTime = uk.localize(dt)
    #time = ts.from_datetime(predTime)

    # gets the satellite data at the predicted time
    #t1 = ts.utc(2014, 1, 24)
    predloc = satellite.at(time)

    #stores the values of the satellites positions printed onto the earths surface (directly below it)
    subsat = wgs84.subpoint(predloc)
    # rounds the results to 8 decimal places for the google map location
    lon = round(subsat.longitude.degrees, 6)
    lat = round(subsat.latitude.degrees, 6)
    return(lon, lat) 


tle = get_tle(25544)
#skyfield
lon, lat = pred_longlat(tle)

#n2yo
satdata = get_info(25544)

print("skyfield = ", lon, lat)
#print("n2yo = ", satdata['positions'][0]['satlongitude'] ,satdata['positions'][0]['satlatitude'])