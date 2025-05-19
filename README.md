# Blockchain Satellite Tracking and Prediction App

A decentralized application for tracking and predicting satellite positions using blockchain technology. This project explores the integration of blockchain technology with space data to promote an open space community.

## Features

- Real-time satellite tracking
- Satellite position prediction
- Decentralized data storage using blockchain
- Interactive web interface
- Smart contract integration for data verification

## Prerequisites

- Python 3.9 or higher
- Node.js and npm
- Ganache (for local blockchain development)
- Truffle (for smart contract deployment)
- MetaMask browser extension

## Installation

1. Clone the repository:
```bash
git clone https://github.com/10lloydj/Blockchain-Satellite-Tracking-and-Prediction-App.git
cd Blockchain-Satellite-Tracking-and-Prediction-App
```

2. Set up Python virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install Truffle globally:
```bash
npm install -g truffle
```

4. Start Ganache (local blockchain):
```bash
ganache-cli -p 8545
```

5. Deploy smart contracts:
```bash
cd Code
truffle migrate
```

## Running the Application

1. Start the Flask application:
```bash
cd Code
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
Blockchain-Satellite-Tracking-and-Prediction-App/
├── Code/
│   ├── contracts/         # Smart contracts
│   ├── flaskr/           # Flask application
│   ├── migrations/       # Truffle migrations
│   ├── tests/           # Test files
│   └── truffle-config.js # Truffle configuration
├── requirements.txt      # Python dependencies
└── venv/                # Python virtual environment
```

## Dependencies

### Python Dependencies
Key dependencies include:
- Flask==3.1.1
- web3==7.11.1
- skyfield==1.53
- requests==2.32.3
- pytz==2025.2
- numpy==2.0.2
- sgp4==2.24
- jplephem==2.22

For a complete list of dependencies, please refer to `requirements.txt`.

### Blockchain Dependencies
- Truffle
- Ganache
- Web3.js
- MetaMask (for browser interaction)

## Environment Setup

Make sure to set up your environment variables:
1. Create a `.env` file in the root directory
2. Add necessary API keys and configuration:
   - N2YO API key
   - Google Maps API key
   - Ethereum network configuration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Skyfield library for astronomical calculations
- N2YO API for satellite data
- Google Maps API for visualization
- SGP4 library for satellite propagation 