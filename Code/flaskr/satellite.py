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
import os
from dotenv import load_dotenv
from pathlib import Path
import logging
from functools import wraps
import time

from datetime import datetime, date, timedelta
import calendar
# timezone package needed for prediction
from pytz import timezone
import pytz
bp = Blueprint('satellite', __name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('satellite.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# N2yo API key
api_key = os.getenv('N2YO_API_KEY')
if not api_key:
    logger.error("N2YO_API_KEY environment variable is not set")
    raise ValueError("N2YO_API_KEY environment variable is not set")

# Skyfield API prediction API
from skyfield.api import load, EarthSatellite, wgs84

#   Smart Contract data set up

# source: https://dev.to/gcrsaldanha/deploy-a-smart-contract-on-ethereum-with-python-truffle-and-web3py-5on
# blockchain smart contract code, possible to do it on this

# ganache address (EVM local blockchain network)
blockchain_address = os.getenv('BLOCKCHAIN_ADDRESS', 'http://127.0.0.1:7545')
# Client instance to interact with the blockchain
web3 = Web3(Web3.HTTPProvider(blockchain_address))
# Set the default account (so we don't need to set the "from" for every transaction call)
web3.eth.defaultAccount = web3.eth.accounts[0]
# Path to the compiled contract Satellites JSON file
contract_artifact_path = os.getenv('CONTRACT_ARTIFACT_PATH', 'Code/flaskr/artifacts/Satellites.json')
compiled_contract_path = PROJECT_ROOT / contract_artifact_path

# Deployed contract address (changes if I migrate --reset the contract)
deployed_contract_address = os.getenv('CONTRACT_ADDRESS')
if not deployed_contract_address:
    logger.error("CONTRACT_ADDRESS environment variable is not set")
    raise ValueError("CONTRACT_ADDRESS environment variable is not set")
deployed_contract_address = web3.to_checksum_address(deployed_contract_address)

# retrieves the smart contract data
try:
    with open(compiled_contract_path) as file:
        contract_json = json.load(file)  # load contract info as JSON
        contract_abi = contract_json['abi']  # fetch contract's abi - necessary to call its functions
except FileNotFoundError:
    logger.error(f"Contract artifact not found at {compiled_contract_path}")
    raise FileNotFoundError(f"Contract artifact not found at {compiled_contract_path}")

# Fetch deployed contract reference
contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)

# Default location coordinates
DEFAULT_LATITUDE = float(os.getenv('DEFAULT_LATITUDE', '53.48095'))
DEFAULT_LONGITUDE = float(os.getenv('DEFAULT_LONGITUDE', '-2.23743'))

def log_route(f):
    """Decorator to log route access and execution time."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Route accessed: {request.method} {request.path}")
        logger.info(f"Request parameters: {request.args.to_dict()}")
        if request.method == 'POST':
            logger.info(f"Form data: {request.form.to_dict()}")
        
        try:
            result = f(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"Route completed in {execution_time:.2f} seconds")
            return result
        except Exception as e:
            logger.error(f"Error in route {request.path}: {str(e)}", exc_info=True)
            raise
    return decorated_function

# satellite home page route
@bp.route('/', methods=('GET', 'POST'))
@log_route
def index():
    logger.info("Accessing satellite index page")
    # near satellite retrieval
    nearsats = get_near()
    # nearsats = ['NO SATELLITES', 'NEAR']
    
    if nearsats is None:
        logger.warning("No nearby satellites found")
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
            logger.warning(f"Missing satellite ID in request")
            flash(error)
        elif (check_sat(get_info(satelliteid)) == False):
            error = 'Satellite ID is invalid.'
            logger.warning(f"Invalid satellite ID: {satelliteid}")
            flash(error)
        elif (check_sat(get_info(satelliteid)) == True):
            logger.info(f"Valid satellite ID found: {satelliteid}")
            session.clear()
            # redirects to the satellite tracking page
            return redirect(url_for('satellite.track', satelliteid=satelliteid))

    return render_template('satellites/index.html', nearsats=nearsats, popnames=popnames, popids=popids)

# about page template route
@bp.route('/about')
@log_route
def about():
    logger.info("Accessing about page")
    return render_template('satellites/About.html')

# track page route with get and post methods
@bp.route('/track', methods=('GET', 'POST'))
@log_route
def track():
    # retrieves the satid variable passed from the home page
    satid = request.args['satelliteid']
    logger.info(f"Tracking satellite ID: {satid}")
    
    # retrieves the satellite data for the satid variable
    satdata = get_info(satid)
    # presents the current time in the current time zone instead of the timestamp
    utc = getUTC(satdata['positions'][0]['timestamp'])

    if request.method == 'POST':
        satid = request.args['satelliteid']
        satdata = get_info(satid)
        # if the save button for the blockchain is selected; saves the satdata to the blockchain network
        if request.form['submit'] == 'save':
            logger.info(f"Saving satellite data for ID: {satid}")
            #variables of the satellite data
            satname = satdata['info']['satname']
            satlon = satdata['positions'][0]['satlongitude']
            satlat = satdata['positions'][0]['satlatitude']
            satelev = satdata['positions'][0]['elevation']
            sataz = satdata['positions'][0]['azimuth']
            satdate = satdata['positions'][0]['timestamp']
            
            # save the data to the smart contract
            tx_hash = saveSat(satdata)
            logger.info(f"Saved to blockchain with transaction hash: {tx_hash}")
            
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
            logger.info(f"Saved to database with block number: {blockNo}")
            # redirects to the blockchain page
            return redirect(url_for('satellite.blockchain', satdata=satdata))

        # if the predict button is selected; it will request the time frame and calculate the longitude and latitude    
        elif request.form['submit'] == 'predict':
            logger.info(f"Predicting position for satellite ID: {satid}")
            # retrieves the satellites TLE (two line elements)
            tle = get_tle(satid)

            # stores the timeframe selected
            period = request.form['predict']
            logger.info(f"Prediction period: {period}")
            
            # retrieves the longitude and latitude of the current tle 
            lon, lat = pred_longlat(tle, period)
            logger.info(f"Predicted position - Longitude: {lon}, Latitude: {lat}")

            satelliteid = satid
            return render_template('satellites/Track.html', lon=lon, lat=lat, utc=utc, satelliteid=satelliteid, satdata=satdata)

    # redirected from the home page, displays the desired satellites data and the location on the map 
    if request.method == 'GET':
        satelliteid = request.args['satelliteid']
        satdata = get_info(satelliteid)
        return render_template('satellites/Track.html', satdata=satdata, utc=utc, satelliteid=satelliteid)

# blockchain page route; retrieves the blockchain database
@bp.route('/blocks')
@log_route
def blockchain():
    logger.info("Accessing blockchain data")
    db = get_db()
    blocks = db.execute(
        'SELECT tx_hash, block_no, date, comment, satname, satid, longitude, latitude, elevation, azimuth, timestamp'
        ' FROM block'
    ).fetchall()
    logger.info(f"Retrieved {len(blocks)} blocks from database")
    # passes the database information to the html page
    return render_template('satellites/viewBlocks.html', blocks=blocks)

# API requires the long and latitude of the user;
# To avoid data security concerns; I will assume the user is using the website from manchester
# Manchester coordinates
#longitude = -2.23743
#latitude = 53.48095

# function retrieves the satellite data to a python dictionary
def get_info(satelliteid):
    logger.info(f"Fetching info for satellite ID: {satelliteid}")
    #formats the satellite id and the api key into the link
    positionurl = f"https://api.n2yo.com/rest/v1/satellite/positions/{satelliteid}/{DEFAULT_LATITUDE}/{DEFAULT_LONGITUDE}/38/1/&apiKey={api_key}"

    # json data parsed into python dictionary
    try:
        with urllib.request.urlopen(positionurl) as responsepos:
            data = json.loads(responsepos.read())
        logger.info(f"Successfully retrieved data for satellite ID: {satelliteid}")
        return data
    except Exception as e:
        logger.error(f"Error fetching satellite data for ID {satelliteid}: {str(e)}")
        raise

# function verifies the existance of the satellite
def check_sat(satdata):
    #get value of a key and checks the satname attribute has a value
    # the url always returns a json
    if satdata['info']['satname'] == None:
        logger.warning("Invalid satellite data - satname is None")
        return False
    else:
        logger.info(f"Valid satellite data for: {satdata['info']['satname']}")
        return True

# function changes the variable types of the satellite data to type string
def satToStr(testsat):
    satarray = [str(testsat['info']['satname']), str(testsat['positions'][0]['satlongitude']), 
    str(testsat['positions'][0]['satlatitude']), str(testsat['positions'][0]['elevation']) , str(testsat['positions'][0]['azimuth']), str(testsat['positions'][0]['timestamp'])]
    return satarray

# corrects the time to UTC form, use when displaying result
def getUTC(timestamp: int):
    utc = datetime.fromtimestamp(timestamp, pytz.UTC).strftime('%Y-%m-%d %H:%M:%S')
    logger.debug(f"Converted timestamp {timestamp} to UTC: {utc}")
    return utc

# saves the current satellite info to the smart contract state memory, thus creating a new block 
def saveSat(testsat):
    logger.info(f"Saving satellite data to blockchain: {testsat['info']['satname']}")
    try:
        #sets the satellite data and creates the hash of the save
        tx_hash = contract.functions.set(0, testsat['info']['satid'], 
            str(testsat['info']['satname']), 
            str(testsat['positions'][0]['satlongitude']), 
            str(testsat['positions'][0]['satlatitude']),
            str(testsat['positions'][0]['elevation']), 
            str(testsat['positions'][0]['azimuth']), 
            str(testsat['positions'][0]['timestamp'])).transact()
        #provides a waiting time for the transacation to be complete and mined
        # i.e stops executing any code until the block's been developed
        web3.eth.waitForTransactionReceipt(tx_hash)
        logger.info(f"Successfully saved to blockchain with transaction hash: {tx_hash}")
        return tx_hash
    except Exception as e:
        logger.error(f"Error saving to blockchain: {str(e)}")
        raise

# calls the smart contract get function to read the current blocks variable states, returns an array
def callSat():
    satinfo = contract.functions.get().call()
    return satinfo

# function retrieves the tle (two line elements) of a satellite
def get_tle(satid):
    logger.info(f"Fetching TLE for satellite ID: {satid}")
    #formats the tle into a json
    tlejson = f"https://api.n2yo.com/rest/v1/satellite/tle/25544&apiKey={api_key}"
    try:
        with urllib.request.urlopen(tlejson) as responsepos:
            data = json.loads(responsepos.read())
        tle = data['tle']
        logger.info("Successfully retrieved TLE data")
        return tle
    except Exception as e:
        logger.error(f"Error fetching TLE data: {str(e)}")
        raise

def pred_longlat(tle, period):
    logger.info(f"Calculating position prediction for period: {period}")
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
    if period == 1:
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
    else:  # period == 70
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
    
    logger.info(f"Predicted position - Longitude: {lon}, Latitude: {lat}")
    return (lon, lat)

# function to retrieve nearby satellite names and information to manchester within 4degrees above
def get_near():
    logger.info("Fetching nearby satellites")
    # json data parsed into python dictionary
    nearjson = f"https://api.n2yo.com/rest/v1/satellite/above/{DEFAULT_LATITUDE}/{DEFAULT_LONGITUDE}/38/4/0/&apiKey={api_key}"

    try:
        with urllib.request.urlopen(nearjson) as responsepos:
            data = json.loads(responsepos.read())
        # retreives the list of satellites and their data
        if data is None:
            logger.warning("No nearby satellites found")
            return None
        else:
            logger.info(f"Retrieved data from N2YO API: {data}")
            nearsat = data.get('above', [])
            logger.info(f"Found {len(nearsat)} nearby satellites")
            return nearsat
    except Exception as e:
        logger.error(f"Error fetching nearby satellites: {str(e)}")
        raise

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

