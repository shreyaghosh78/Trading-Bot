import os
from dotenv import load_dotenv

load_dotenv()

# Binance Testnet Configuration
TESTNET_BASE_URL = "https://testnet.binancefuture.com"
API_KEY = os.getenv('BINANCE_TESTNET_API_KEY')
API_SECRET = os.getenv('BINANCE_TESTNET_API_SECRET')

# Logging Configuration
LOG_FILE = "logs/trading.log"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Trading Configuration
DEFAULT_SYMBOL = "BTCUSDT"
DEFAULT_QUANTITY = 0.001
