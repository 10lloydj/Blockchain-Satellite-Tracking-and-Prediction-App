import os
import logging
from web3 import Web3
from pathlib import Path
import json

logger = logging.getLogger(__name__)

def get_blockchain_config():
    """
    Returns blockchain configuration based on the current environment.
    """
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        # Production configuration (Render deployment)
        return {
            'address': os.getenv('BLOCKCHAIN_ADDRESS'),
            'network': 'sepolia',  # or whatever testnet you're using
            'contract_address': os.getenv('CONTRACT_ADDRESS'),
            'artifact_path': os.getenv('CONTRACT_ARTIFACT_PATH', 'Code/flaskr/artifacts/Satellites.json')
        }
    else:
        # Development configuration (local Ganache)
        return {
            'address': 'http://127.0.0.1:7545',
            'network': 'local',
            'contract_address': os.getenv('CONTRACT_ADDRESS'),
            'artifact_path': 'Code/flaskr/artifacts/Satellites.json'
        }

def init_web3():
    """
    Initialize Web3 connection based on environment configuration.
    """
    config = get_blockchain_config()
    
    # Initialize Web3
    web3 = Web3(Web3.HTTPProvider(config['address']))
    
    if not web3.is_connected():
        logger.error(f"Failed to connect to blockchain at {config['address']}")
        raise ConnectionError(f"Failed to connect to blockchain at {config['address']}")
    
    logger.info(f"Connected to {config['network']} network at {config['address']}")
    
    # Set default account for local development
    if config['network'] == 'local':
        web3.eth.defaultAccount = web3.eth.accounts[0]
    
    return web3

def get_contract(web3):
    """
    Get the contract instance based on environment configuration.
    """
    config = get_blockchain_config()
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Load contract ABI
    try:
        with open(project_root / config['artifact_path']) as file:
            contract_json = json.load(file)
            contract_abi = contract_json['abi']
    except FileNotFoundError:
        logger.error(f"Contract artifact not found at {config['artifact_path']}")
        raise FileNotFoundError(f"Contract artifact not found at {config['artifact_path']}")
    
    # Get contract address
    contract_address = web3.to_checksum_address(config['contract_address'])
    
    # Create contract instance
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
    
    return contract 