import logging
import sys
import time
from datetime import datetime
from binance import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import config

class BasicBot:
    def __init__(self, api_key=None, api_secret=None, testnet=True):
        """
        Initialize the trading bot
        
        Args:
            api_key (str): Binance API Key
            api_secret (str): Binance API Secret
            testnet (bool): Use testnet environment
        """
        self.api_key = api_key or config.API_KEY
        self.api_secret = api_secret or config.API_SECRET
        self.testnet = testnet
        
        # Setup logging
        self._setup_logging()
        
        # Initialize client
        try:
            self.client = Client(self.api_key, self.api_secret, testnet=self.testnet)
            self.logger.info("Trading bot initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize client: {e}")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format=config.LOG_FORMAT,
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def validate_inputs(self, symbol, quantity, side, order_type, **kwargs):
        """
        Validate trading inputs
        
        Args:
            symbol (str): Trading pair symbol
            quantity (float): Order quantity
            side (str): BUY or SELL
            order_type (str): Order type (MARKET, LIMIT, STOP_LIMIT)
            **kwargs: Additional parameters
        
        Returns:
            bool: True if inputs are valid
        """
        valid_sides = ['BUY', 'SELL']
        valid_types = ['MARKET', 'LIMIT', 'STOP_LIMIT']
        
        if side.upper() not in valid_sides:
            self.logger.error(f"Invalid side: {side}. Must be one of {valid_sides}")
            return False
        
        if order_type.upper() not in valid_types:
            self.logger.error(f"Invalid order type: {order_type}. Must be one of {valid_types}")
            return False
        
        if quantity <= 0:
            self.logger.error("Quantity must be positive")
            return False
        
        # Validate symbol exists
        try:
            exchange_info = self.client.futures_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols']]
            if symbol not in symbols:
                self.logger.error(f"Invalid symbol: {symbol}")
                return False
        except Exception as e:
            self.logger.error(f"Error validating symbol: {e}")
            return False
        
        # Validate limit price for limit orders
        if order_type.upper() in ['LIMIT', 'STOP_LIMIT']:
            if 'price' not in kwargs or kwargs['price'] <= 0:
                self.logger.error("Limit price required for LIMIT and STOP_LIMIT orders")
                return False
        
        # Validate stop price for stop-limit orders
        if order_type.upper() == 'STOP_LIMIT':
            if 'stop_price' not in kwargs or kwargs['stop_price'] <= 0:
                self.logger.error("Stop price required for STOP_LIMIT orders")
                return False
        
        return True
    
    def place_market_order(self, symbol, side, quantity):
        """
        Place a market order
        
        Args:
            symbol (str): Trading pair symbol
            side (str): BUY or SELL
            quantity (float): Order quantity
        
        Returns:
            dict: Order response
        """
        try:
            self.logger.info(f"Placing market order: {side} {quantity} {symbol}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            
            self.logger.info(f"Market order placed successfully: {order}")
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API Error in market order: {e}")
            return None
        except BinanceOrderException as e:
            self.logger.error(f"Binance Order Error in market order: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in market order: {e}")
            return None
    
    def place_limit_order(self, symbol, side, quantity, price):
        """
        Place a limit order
        
        Args:
            symbol (str): Trading pair symbol
            side (str): BUY or SELL
            quantity (float): Order quantity
            price (float): Limit price
        
        Returns:
            dict: Order response
        """
        try:
            self.logger.info(f"Placing limit order: {side} {quantity} {symbol} @ {price}")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=price,
                timeInForce='GTC'  # Good Till Cancelled
            )
            
            self.logger.info(f"Limit order placed successfully: {order}")
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API Error in limit order: {e}")
            return None
        except BinanceOrderException as e:
            self.logger.error(f"Binance Order Error in limit order: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in limit order: {e}")
            return None
    
    def place_stop_limit_order(self, symbol, side, quantity, price, stop_price):
        """
        Place a stop-limit order (Bonus feature)
        
        Args:
            symbol (str): Trading pair symbol
            side (str): BUY or SELL
            quantity (float): Order quantity
            price (float): Limit price
            stop_price (float): Stop price
        
        Returns:
            dict: Order response
        """
        try:
            self.logger.info(f"Placing stop-limit order: {side} {quantity} {symbol} @ {price} (stop: {stop_price})")
            
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                timeInForce='GTC'
            )
            
            self.logger.info(f"Stop-limit order placed successfully: {order}")
            return order
            
        except BinanceAPIException as e:
            self.logger.error(f"Binance API Error in stop-limit order: {e}")
            return None
        except BinanceOrderException as e:
            self.logger.error(f"Binance Order Error in stop-limit order: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error in stop-limit order: {e}")
            return None
    
    def get_order_status(self, symbol, order_id):
        """
        Get order status
        
        Args:
            symbol (str): Trading pair symbol
            order_id (int): Order ID
        
        Returns:
            dict: Order status
        """
        try:
            status = self.client.futures_get_order(symbol=symbol, orderId=order_id)
            self.logger.info(f"Order status: {status}")
            return status
        except Exception as e:
            self.logger.error(f"Error getting order status: {e}")
            return None
    
    def get_account_balance(self):
        """
        Get USDT balance
        
        Returns:
            float: USDT balance
        """
        try:
            balance = self.client.futures_account_balance()
            usdt_balance = next((item for item in balance if item['asset'] == 'USDT'), None)
            if usdt_balance:
                self.logger.info(f"USDT Balance: {usdt_balance['balance']}")
                return float(usdt_balance['balance'])
            return 0.0
        except Exception as e:
            self.logger.error(f"Error getting balance: {e}")
            return 0.0
    
    def place_order(self, symbol, side, order_type, quantity, **kwargs):
        """
        Main order placement method
        
        Args:
            symbol (str): Trading pair symbol
            side (str): BUY or SELL
            order_type (str): MARKET, LIMIT, or STOP_LIMIT
            quantity (float): Order quantity
            **kwargs: Additional parameters (price, stop_price)
        
        Returns:
            dict: Order response
        """
        # Validate inputs
        if not self.validate_inputs(symbol, quantity, side, order_type, **kwargs):
            return None
        
        # Place order based on type
        order_type = order_type.upper()
        
        if order_type == 'MARKET':
            return self.place_market_order(symbol, side, quantity)
        
        elif order_type == 'LIMIT':
            if 'price' not in kwargs:
                self.logger.error("Price required for limit orders")
                return None
            return self.place_limit_order(symbol, side, quantity, kwargs['price'])
        
        elif order_type == 'STOP_LIMIT':
            if 'price' not in kwargs or 'stop_price' not in kwargs:
                self.logger.error("Price and stop_price required for stop-limit orders")
                return None
            return self.place_stop_limit_order(symbol, side, quantity, kwargs['price'], kwargs['stop_price'])
        
        else:
            self.logger.error(f"Unsupported order type: {order_type}")
            return None

def main():
    """Command-line interface for the trading bot"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Binance Futures Trading Bot')
    
    # Required arguments
    parser.add_argument('--symbol', required=True, help='Trading symbol (e.g., BTCUSDT)')
    parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    parser.add_argument('--order-type', required=True, choices=['MARKET', 'LIMIT', 'STOP_LIMIT'], 
                       help='Order type')
    
    # Optional arguments
    parser.add_argument('--price', type=float, help='Limit price (for LIMIT and STOP_LIMIT orders)')
    parser.add_argument('--stop-price', type=float, help='Stop price (for STOP_LIMIT orders)')
    parser.add_argument('--api-key', help='Binance API Key (optional if in environment)')
    parser.add_argument('--api-secret', help='Binance API Secret (optional if in environment)')
    
    args = parser.parse_args()
    
    # Initialize bot
    try:
        bot = BasicBot(api_key=args.api_key, api_secret=args.api_secret)
    except Exception as e:
        print(f"Failed to initialize trading bot: {e}")
        return
    
    # Prepare order parameters
    order_params = {}
    if args.price:
        order_params['price'] = args.price
    if args.stop_price:
        order_params['stop_price'] = args.stop_price
    
    # Display account balance
    balance = bot.get_account_balance()
    print(f"Current USDT Balance: {balance}")
    
    # Place order
    print(f"\nPlacing {args.order_type} order:")
    print(f"Symbol: {args.symbol}")
    print(f"Side: {args.side}")
    print(f"Quantity: {args.quantity}")
    if args.price:
        print(f"Price: {args.price}")
    if args.stop_price:
        print(f"Stop Price: {args.stop_price}")
    
    confirmation = input("\nConfirm order? (y/n): ")
    if confirmation.lower() != 'y':
        print("Order cancelled")
        return
    
    # Execute order
    result = bot.place_order(
        symbol=args.symbol,
        side=args.side,
        order_type=args.order_type,
        quantity=args.quantity,
        **order_params
    )
    
    if result:
        print(f"\n✅ Order placed successfully!")
        print(f"Order ID: {result['orderId']}")
        print(f"Status: {result['status']}")
        
        # Display order details
        if 'price' in result:
            print(f"Price: {result['price']}")
        if 'stopPrice' in result:
            print(f"Stop Price: {result['stopPrice']}")
        
        # Check order status after a brief delay
        print("\nChecking order status...")
        time.sleep(2)
        status = bot.get_order_status(args.symbol, result['orderId'])
        if status:
            print(f"Current Status: {status['status']}")
            if status['status'] == 'FILLED':
                print(f"Executed Quantity: {status['executedQty']}")
                if 'avgPrice' in status:
                    print(f"Average Price: {status['avgPrice']}")
    
    else:
        print(f"\n❌ Failed to place order. Check logs for details.")

if __name__ == "__main__":
    main()
