"""
Binance Futures API client module
"""

import os
import time
import hmac
import hashlib
import urllib.parse
from typing import Dict, Optional, Any
from datetime import datetime

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BinanceFuturesClient:
    """
    Client for interacting with Binance Futures Testnet API
    """
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize the Binance Futures client.
        
        Args:
            api_key: Binance API key (optional, reads from env if not provided)
            api_secret: Binance API secret (optional, reads from env if not provided)
        """
        self.api_key = api_key or os.getenv('API_KEY')
        self.api_secret = api_secret or os.getenv('API_SECRET')
        self.base_url = os.getenv('BINANCE_FUTURES_URL', 'https://testnet.binancefuture.com')
        
        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API key and secret are required. "
                "Set them in .env file or pass as arguments."
            )
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        })
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for API request.
        
        Args:
            params: Request parameters dictionary
            
        Returns:
            Generated signature string
        """
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make authenticated request to Binance API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            Exception: On API error or network failure
        """
        url = f"{self.base_url}{endpoint}"
        
        if params is None:
            params = {}
        
        # Add timestamp for authenticated endpoints
        if 'timestamp' not in params:
            server_time = self.session.get(
              f"{self.base_url}/fapi/v1/time"
              ).json()['serverTime']

            params['timestamp'] = server_time
        
        # Generate signature
        params['signature'] = self._generate_signature(params)
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == 'POST':
                response = self.session.post(url, params=params, timeout=10)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            print("Status Code:", response.status_code)
            print("Response:", response.text)

            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise Exception("Network timeout: Request took too long to complete")
        except requests.exceptions.ConnectionError:
            raise Exception("Network error: Failed to connect to Binance API")
        except requests.exceptions.HTTPError as e:
            # Parse Binance error response
            try:
                error_data = response.json()
                error_msg = error_data.get('msg', str(e))
                raise Exception(f"Binance API error: {error_msg}")
            except:
                raise Exception(f"HTTP error: {str(e)}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict:
        """
        Get exchange information for a symbol.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Exchange information dictionary
        """
        endpoint = '/fapi/v1/exchangeInfo'
        params = {'symbol': symbol} if symbol else {}
        return self._make_request('GET', endpoint, params)
    
    def get_account_balance(self) -> Dict:
        """
        Get account balance information.
        
        Returns:
            Account balance dictionary
        """
        endpoint = '/fapi/v2/account'
        params = {'timestamp': int(time.time() * 1000)}
        return self._make_request('GET', endpoint, params)
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = 'GTC'
    ) -> Dict:
        """
        Place an order on Binance Futures.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            order_type: 'MARKET' or 'LIMIT'
            quantity: Order quantity
            price: Price for LIMIT orders (required for LIMIT)
            time_in_force: Time in force for LIMIT orders ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order response dictionary
        """
        endpoint = '/fapi/v1/order'
        
        params = {
            'symbol': symbol.upper(),
            'side': side.upper(),
            'type': order_type.upper(),
            'quantity': float(quantity)
        }
        
        if order_type.upper() == 'LIMIT':
            if price is None:
                raise ValueError("Price is required for LIMIT orders")
            params['price'] = float(price)
            params['timeInForce'] = time_in_force
        
        return self._make_request('POST', endpoint, params)
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict:
        """
        Get status of a specific order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
            
        Returns:
            Order status dictionary
        """
        endpoint = '/fapi/v1/order'
        params = {
            'symbol': symbol.upper(),
            'orderId': order_id
        }
        return self._make_request('GET', endpoint, params)