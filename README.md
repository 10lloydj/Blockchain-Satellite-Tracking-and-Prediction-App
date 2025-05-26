# Blockchain Satellite Tracking and Prediction App

A decentralized application for tracking and predicting satellite positions using blockchain technology. This project explores the integration of blockchain technology with space data to promote an open space community.

---

## Features

- Real-time satellite tracking
- Satellite position prediction
- Decentralized data storage using blockchain
- Interactive web interface
- Smart contract integration for data verification
- Comprehensive logging system for debugging and monitoring

---

## 🌐 Live Demo

[Visit the live project here](https://blockchain-satellite-prediction-app.onrender.com/)

---

## Prerequisites

- Python 3.9 or higher
- Node.js and npm
- Ganache (for local blockchain development)
- Truffle (for smart contract deployment)
- MetaMask browser extension

---

## Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/10lloydj/Blockchain-Satellite-Tracking-and-Prediction-App.git
    cd Blockchain-Satellite-Tracking-and-Prediction-App
    ```

2. **Set up Python virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Install Truffle globally:**
    ```bash
    npm install -g truffle
    ```

4. **Start Ganache (local blockchain):**
    ```bash
    ganache --port 7545
    ```
    > **Note:** The app expects Ganache to run on port 7545 by default. You can change this in your `.env` if needed.

5. **Deploy smart contracts:**
    ```bash
    cd Code
    truffle migrate
    ```

---

## Running the Application

1. **Set up environment variables:**
    - Copy `.env.example` to `.env` and fill in your secrets and API keys.
    - **Never commit your `.env` file.**

2. **Start the Flask application:**
    ```bash
    cd Code
    export FLASK_APP=flaskr
    export FLASK_ENV=development
    flask run
    ```

3. **Open your web browser and navigate to:**
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

---

## Dependencies

### Python Dependencies
Key dependencies include:
- Flask
- web3
- skyfield
- requests
- pytz
- numpy
- sgp4
- jplephem
- python-dotenv

For a complete list of dependencies, see `requirements.txt`.

### Blockchain Dependencies
- Truffle
- Ganache
- Web3.js
- MetaMask (for browser interaction)

---

## Environment Setup

1. **Create a `.env` file** in the root directory using `.env.example` as a template.
2. **Add necessary API keys and configuration:**
    - `N2YO_API_KEY`
    - `GOOGLE_MAPS_API_KEY`
    - `BLOCKCHAIN_ADDRESS`
    - `CONTRACT_ADDRESS`
    - `CONTRACT_ARTIFACT_PATH`
    - `DEFAULT_LATITUDE`, `DEFAULT_LONGITUDE`
    - `SECRET_KEY` (generate securely)
    - Any other required variables as shown in `.env.example`

---

## Security & Best Practices

- **Never commit your `.env` file or any secrets.**
- All sensitive values are loaded from environment variables.
- The app is safe to share and deploy as long as you keep your `.env` private.
- Set all secrets in Render's dashboard for production.

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- Skyfield library for astronomical calculations
- N2YO API for satellite data
- Google Maps API for visualization
- SGP4 library for satellite propagation 

---
