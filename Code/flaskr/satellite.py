# flask packages
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from flaskr.auth import login_required
from flaskr.db import get_db
# json file extraction packages
import urllib, json
import urllib.request, json
# blockchain packages
from web3 import Web3, HTTPProvider

from datetime import datetime, date, timedelta
import calendar
# timezone package needed for prediction
from pytz import timezone
bp = Blueprint('satellite', __name__)

# N2yo API key
api_key = 'KQ9N7M-XWZL5A-NV4CAK-4NG8'
# Skyfield API prediction API
from skyfield.api import load, EarthSatellite, wgs84
#   Smart Contract data set up

# source: https://dev.to/gcrsaldanha/deploy-a-smart-contract-on-ethereum-with-python-truffle-and-web3py-5on
# blockchain smart contract code, possible to do it on this


# ganache address (EVM local blockchain network)
blockchain_address = 'http://127.0.0.1:7545'
# Client instance to interact with the blockchain
web3 = Web3(Web3.HTTPProvider(blockchain_address))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
# Path to the compiled contract Satellites JSON file
compiled_contract_path = '/Users/jordanlloyd/Satellite/Code/flaskr/artifacts/Satellites.json'
# Deployed contract address (changes if I migrate --reset the contract)
deployed_contract_address = '0x26aDB61B71Dfe8eE3d9AA1Dd1eE6Ba0BE6bB9238'

# retrieves the smart contract data
with open(compiled_contract_path) as file:
    contract_json = json.load(file)  # load contract info as JSON
    contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions

# Fetch deployed contract reference
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

# satellite home page route
@bp.route('/satelliteindex', methods=('GET', 'POST'))
def index():
    # near satellite retrieval
    nearsats = get_near()
    if nearsats is None:
        nearsats = ['NO SATELLITES', 'NEAR']
    # arrays of popular satellite details
    popnames = ['Space Station', 'SES 1', 'NOAA 19', 'GOES 13', 'TERRA', 'AQUA']
    popids = [25544, 36516, 25338, 29155, 25994, 27424]


    if request.method == 'POST':
        # NORAD ID track verification
        satelliteid = request.form['satelliteid']
        error = None
        if not satelliteid:
            error = 'Satellite ID is required.'
            flash(error)

        elif (check_sat(get_info(satelliteid)) == False):
            error = 'Satellite ID is invalid.'
            flash(error)
        elif (check_sat(get_info(satelliteid)) == True):
            session.clear()
            # redirects to the satellite tracking page
            return redirect(url_for('satellite.track', satelliteid=satelliteid))

    return render_template('satellites/index.html', nearsats=nearsats, popnames=popnames, popids=popids)

# about page template route
@bp.route('/about')
def about():
    return render_template('satellites/About.html')

# track page route with get and post methods
@bp.route('/track', methods=('GET', 'POST'))
def track():
    # retrieves the satid variable passed from the home page
    satid = request.args['satelliteid'] 
    # retrieves the satellite data for the satid variable
    satdata = get_info(satid)
    # presents the current time in the current time zone instead of the timestamp
    utc = getUTC(satdata['positions'][0]['timestamp'])

    if request.method == 'POST':
        satid = request.args['satelliteid'] 
        satdata = get_info(satid)
        # if the save button for the blockchain is selected; saves the satdata to the blockchain network

        if request.form['submit'] == 'save':

            #variables of the satellite data
            satname = satdata['info']['satname']
            satlon = satdata['positions'][0]['satlongitude']
            satlat = satdata['positions'][0]['satlatitude']
            satelev = satdata['positions'][0]['elevation']
            sataz = satdata['positions'][0]['azimuth']
            satdate = satdata['positions'][0]['timestamp']
            
            # save the data to the smart contract
            tx_hash = saveSat(satdata)
            # retrieves the latest/ current block number
            blockNo = web3.eth.blockNumber
            satComment = request.form['satComment']
            cdate = datetime.now()

            # save the block number and comment into the database
            # we can access the satdata using the block number
            db = get_db()
            db.execute(
                'INSERT INTO block (tx_hash, block_no, date, comment, satname, satid, longitude, latitude, elevation, azimuth, timestamp)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (tx_hash, blockNo, cdate.strftime("%d/%m/%Y %H:%M:%S"), satComment, satname, satid, satlon, satlat, satelev, sataz, getUTC(satdate))
            )
            db.commit()
            # redirects to the blockchain page
            return redirect(url_for('satellite.blockchain', satdata=satdata ))

        # if the predict button is selected; it will request the time frame and calculate the longitude and latitude    
        elif request.form['submit'] == 'predict':
            satid = request.args['satelliteid'] 
            # retrieves the satellites TLE (two line elements)
            tle = get_tle(satid)

            # stores the timeframe selected
            period = request.form['predict'] 
                                    
            # retrieves the longitude and latitude of the current tle 
            lon, lat = pred_longlat(tle, period)

            satelliteid = satid

            return render_template('satellites/Track.html',lon=lon, lat=lat, utc=utc, satelliteid=satelliteid, satdata=satdata )
 
    #  redirected from the home page, displays the desired satellites data and the location on the map 
    if request.method == 'GET':
        satelliteid = request.args['satelliteid']
    
        satdata = get_info(satelliteid)

        return render_template('satellites/Track.html', satdata=satdata, utc=utc, satelliteid=satelliteid)

# blockchain page route; retrieves the blockchain database
@bp.route('/blocks')
def blockchain():
    db = get_db()
    blocks = db.execute(
        'SELECT tx_hash, block_no, date, comment, satname, satid, longitude, latitude, elevation, azimuth, timestamp'
        ' FROM block'
    ).fetchall()
    # passes the database information to the html page
    return render_template('satellites/viewBlocks.html', blocks=blocks)


# API requires the long and latitude of the user;
# To avoid data security concerns; I will assume the user is using the website from manchester
# Manchester coordinates
#longitude = -2.23743
#latitude = 53.48095

# function retrieves the satellite data to a python dictionary
def get_info(satelliteid):
    #formats the satellite id and the api key into the link
    positionurl = "https://api.n2yo.com/rest/v1/satellite/positions/{}/53.48095/-2.23743/38/1/&apiKey={}".format(satelliteid, api_key)

    # json data parsed into python dictionary
    with urllib.request.urlopen(positionurl) as responsepos:
        data = json.loads(responsepos.read())

    return data

# function verifies the existance of the satellite
def check_sat(satdata):
    #get value of a key and checks the satname attribute has a value
    # the url always returns a json
    if satdata['info']['satname'] == None:
        return False
    else:
        return True

# function changes the variable types of the satellite data to type string
def satToStr(testsat):
    satarray = [str(testsat['info']['satname']), str(testsat['positions'][0]['satlongitude']), 
    str(testsat['positions'][0]['satlatitude']), str(testsat['positions'][0]['elevation']) , str(testsat['positions'][0]['azimuth']), str(testsat['positions'][0]['timestamp'])]
    return satarray

# corrects the time to UTC form, use when displaying result
def getUTC(timestamp: int):
    utc = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return utc

# saves the current satellite info to the smart contract state memory, thus creating a new block 
def saveSat(testsat):
    #sets the satellite data and creates the hash of the save
    tx_hash = contract.functions.set(0 ,testsat['info']['satid'], str(testsat['info']['satname']), str(testsat['positions'][0]['satlongitude']), str(testsat['positions'][0]['satlatitude']),
    str(testsat['positions'][0]['elevation']), str(testsat['positions'][0]['azimuth']), str(testsat['positions'][0]['timestamp'])).transact()
    #provides a waiting time for the transacation to be complete and mined
    # i.e stops executing any code until the block's been developed
    web3.eth.waitForTransactionReceipt(tx_hash)
    return tx_hash

# calls the smart contract get function to read the current blocks variable states, returns an array
def callSat():
    satinfo = contract.functions.get().call()
    return satinfo

# function retrieves the tle (two line elements) of a satellite
def get_tle(satid):
    #formats the tle into a json
    tlejson = "https://api.n2yo.com/rest/v1/satellite/tle/25544&apiKey={}".format(api_key)
    with urllib.request.urlopen(tlejson) as responsepos:
        data = json.loads(responsepos.read())
    tle = data['tle']
    return(tle)

def pred_longlat(tle, period):
    #time abstraction
    ts = load.timescale()
    # splits the TLE elements into their lines
    line1, line2 = tle.splitlines()
    # represents the tle data as the satellite
    satellite = EarthSatellite(line1, line2)
    #utc(year, month=1, day=1, hour=0, minute=0, second=0.0)
    #time = ts.utc(year, month, day, hour)
    # retrieves the correct timezone
    uk = timezone('Europe/London')

    # adds time or dates to the current datetime
    if period == 1 :
        dt = datetime.now() + timedelta(hours=1)
    elif period == 2:
        dt = datetime.now() + timedelta(hours=2)
    elif period == 4:
        dt = datetime.now() + timedelta(hours=4)
    elif period == 6:
        dt = datetime.now() + timedelta(hours=6)
    elif period == 12:
        dt = datetime.now() + timedelta(hours=12)
    elif period == 24:
        dt = datetime.now() + timedelta(days=1)
    elif period == 40:
        dt = datetime.now() + timedelta(days=4)
    else: # period == 70
        dt = datetime.now() + timedelta(days=7)

    predTime = uk.localize(dt)
    time = ts.from_datetime(predTime)

    # gets the satellite data at the predicted time
    #t1 = ts.utc(2014, 1, 24)
    predloc = satellite.at(time)

    #stores the values of the satellites positions printed onto the earths surface (directly below it)
    subsat = wgs84.subpoint(predloc)
    # rounds the results to 8 decimal places for the google map location
    lon = round(subsat.longitude.degrees, 6)
    lat = round(subsat.latitude.degrees, 6)
    return(lon, lat)    

# function to retrieve nearby satellite names and information to manchester within 4degrees above
def get_near():
    # json data parsed into python dictionary
    nearjson = "https://api.n2yo.com/rest/v1/satellite/above/53.48095/-2.23743/38/4/0/&apiKey={}".format(api_key)

    with urllib.request.urlopen(nearjson) as responsepos:
        data = json.loads(responsepos.read())
    # retreives the list of satellites and their data
    # validates there are some satellites, to prevent errors
    if data is None:
        return None
    else:
        nearsat = data['above']
        return nearsat


def setPredtime(period):
    day = date.today().day
    month = date.today().month
    year = date.today().year
    now = datetime.now()
    hour = now.hour
    # make shift 'switch' and validation to ensure the time is correct for prediction

    # 1hr
    if(period == 1):
        hour = hour + 1
        if (hour >= 24 ):
            day = day + 1
            hour = hour - 24
            if (day > calendar.monthrange(year, month)[1] ):
                day = day - calendar.monthrange(year, month)[1]
                month = month + 1
                if (month >= 13):
                    month = 1
                    year = year + 1
    # 2hrs
    elif (period == 2):
        hour = hour + 2
        if (hour >= 24 ):
            day = day + 1
            hour = hour - 24
            if (day > calendar.monthrange(year, month)[1] ):
                day = day - calendar.monthrange(year, month)[1]
                month = month + 1
                if (month >= 13):
                    month = 1
                    year = year + 1
    # 4hrs
    elif(period == 4):
        hour = hour + 4
        if (hour >= 24 ):
            day = day + 1
            hour = hour - 24
            if (day > calendar.monthrange(year, month)[1] ):
                day = day - calendar.monthrange(year, month)[1]
                month = month + 1
                if (month >= 13):
                    month = 1
                    year = year + 1
    # 6hrs
    elif(period == 6):
        hour = hour + 6
        if (hour >= 24 ):
            day = day + 1
            hour = hour - 24
            if (day > calendar.monthrange(year, month)[1]):
                day = day - calendar.monthrange(year, month)[1]
                month = month + 1
                if (month >= 13):
                    month = 1
                    year = year + 1
    # 12hrs
    elif(period == 12):
        hour = hour + 12
        if (hour >= 24 ):
            day = day + 1
            hour = hour - 24
            if (day > calendar.monthrange(year, month)[1] ):
                day = day - calendar.monthrange(year, month)[1]
                month = month + 1
                if (month >= 13):
                    month = 1
                    year = year + 1
    # 1day
    elif(period == 24):
        day = day + 1
        if (day > calendar.monthrange(year, month)[1] ):
            day = day - calendar.monthrange(year, month)[1]
            month = month + 1
            if (month >= 13):
                month = 1
                year = year + 1
    # 4days
    elif(period == 40):
        day = day + 4
        if (day > calendar.monthrange(year, month)[1] ):
            day = day - calendar.monthrange(year, month)[1]
            month = month + 1
            if (month >= 13):
                month = 1
                year = year + 1    
    # 7days
    elif(period == 70):
        day = day + 7
        if (day > calendar.monthrange(year, month)[1] ):
            day = day - calendar.monthrange(year, month)[1]
            month = month + 1
            if (month >= 13):
                month = 1
                year = year + 1    

    return (year, month, day, hour)

