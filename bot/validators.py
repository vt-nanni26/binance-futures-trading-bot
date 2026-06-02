"""
Input validation module for trading bot
"""

import re
from typing import Tuple, Optional


class OrderValidator:
    """
    Validator for order inputs
    """
    
    # Valid trading pairs on Binance Futures
    VALID_SYMBOLS = {
        'BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'XRPUSDT',
        'SOLUSDT', 'DOGEUSDT', 'DOTUSDT', 'MATICUSDT', 'LINKUSDT'
    }
    
    @classmethod
    def validate_symbol(cls, symbol: str) -> Tuple[bool, Optional[str]]:
        """
        Validate trading pair symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not symbol:
            return False, "Symbol cannot be empty"
        
        symbol = symbol.upper()
        
        # Check if symbol format is valid (e.g., BTCUSDT)
        if not re.match(r'^[A-Z]{2,10}USDT$', symbol):
            return False, "Symbol must end with 'USDT' (e.g., BTCUSDT, ETHUSDT)"
        
        # Note: In production, you might want to fetch this dynamically
        if symbol not in cls.VALID_SYMBOLS:
            return False, f"Symbol '{symbol}' may not be supported. Supported symbols: {', '.join(cls.VALID_SYMBOLS)}"
        
        return True, None
    
    @classmethod
    def validate_side(cls, side: str) -> Tuple[bool, Optional[str]]:
        """
        Validate order side.
        
        Args:
            side: Order side (BUY/SELL)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not side:
            return False, "Side cannot be empty"
        
        side = side.upper()
        
        if side not in ['BUY', 'SELL']:
            return False, "Side must be either 'BUY' or 'SELL'"
        
        return True, None
    
    @classmethod
    def validate_order_type(cls, order_type: str) -> Tuple[bool, Optional[str]]:
        """
        Validate order type.
        
        Args:
            order_type: Order type (MARKET/LIMIT)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not order_type:
            return False, "Order type cannot be empty"
        
        order_type = order_type.upper()
        
        if order_type not in ['MARKET', 'LIMIT']:
            return False, "Order type must be either 'MARKET' or 'LIMIT'"
        
        return True, None
    
    @classmethod
    def validate_quantity(cls, quantity: float) -> Tuple[bool, Optional[str]]:
        """
        Validate order quantity.
        
        Args:
            quantity: Order quantity
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if quantity is None:
            return False, "Quantity cannot be empty"
        
        try:
            quantity = float(quantity)
        except (ValueError, TypeError):
            return False, "Quantity must be a valid number"
        
        if quantity <= 0:
            return False, "Quantity must be greater than 0"
        
        if quantity > 1000:  # Reasonable upper limit for testnet
            return False, "Quantity is too large. Maximum allowed: 1000"
        
        return True, None
    
    @classmethod
    def validate_price(cls, price: float, is_limit: bool) -> Tuple[bool, Optional[str]]:
        """
        Validate order price.
        
        Args:
            price: Order price
            is_limit: Whether this is a LIMIT order
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not is_limit:
            return True, None  # Price not required for MARKET orders
        
        if price is None:
            return False, "Price is required for LIMIT orders"
        
        try:
            price = float(price)
        except (ValueError, TypeError):
            return False, "Price must be a valid number"
        
        if price <= 0:
            return False, "Price must be greater than 0"
        
        return True, None
    
    @classmethod
    def validate_all(
        cls,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None
    ) -> Tuple[bool, list]:
        """
        Validate all order parameters.
        
        Args:
            symbol: Trading pair symbol
            side: Order side
            order_type: Order type
            quantity: Order quantity
            price: Order price (optional)
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Validate symbol
        is_valid, error = cls.validate_symbol(symbol)
        if not is_valid:
            errors.append(error)
        
        # Validate side
        is_valid, error = cls.validate_side(side)
        if not is_valid:
            errors.append(error)
        
        # Validate order type
        is_valid, error = cls.validate_order_type(order_type)
        if not is_valid:
            errors.append(error)
        
        # Validate quantity
        is_valid, error = cls.validate_quantity(quantity)
        if not is_valid:
            errors.append(error)
        
        # Validate price
        is_valid, error = cls.validate_price(price, order_type.upper() == 'LIMIT')
        if not is_valid:
            errors.append(error)
        
        return len(errors) == 0, errors