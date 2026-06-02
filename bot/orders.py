"""
Order management module
"""

from typing import Dict, Optional
from decimal import Decimal, ROUND_DOWN

from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logging


class OrderManager:
    """
    Manages order placement and tracking
    """
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize OrderManager with API client.
        
        Args:
            client: BinanceFuturesClient instance
        """
        self.client = client
        self.logger = setup_logging()
    
    def format_order_summary(self, order_params: Dict) -> str:
        """
        Format order parameters for display.
        
        Args:
            order_params: Order parameters dictionary
            
        Returns:
            Formatted order summary string
        """
        summary = [
            "=" * 50,
            "ORDER REQUEST SUMMARY",
            "=" * 50,
            f"Symbol:        {order_params.get('symbol', 'N/A')}",
            f"Side:          {order_params.get('side', 'N/A')}",
            f"Type:          {order_params.get('type', 'N/A')}",
            f"Quantity:      {order_params.get('quantity', 'N/A')}"
        ]
        
        if order_params.get('price'):
            summary.append(f"Price:         {order_params['price']}")
        
        if order_params.get('timeInForce'):
            summary.append(f"Time In Force: {order_params['timeInForce']}")
        
        summary.append("=" * 50)
        
        return "\n".join(summary)
    
    def format_order_response(self, response: Dict) -> str:
        """
        Format order response for display.
        
        Args:
            response: Order response dictionary
            
        Returns:
            Formatted order response string
        """
        # Extract relevant fields
        order_id = response.get('orderId', 'N/A')
        status = response.get('status', 'N/A')
        executed_qty = response.get('executedQty', '0')
        orig_qty = response.get('origQty', '0')
        avg_price = response.get('avgPrice', '0')
        
        # Calculate fill percentage
        try:
            fill_pct = (float(executed_qty) / float(orig_qty)) * 100 if float(orig_qty) > 0 else 0
        except:
            fill_pct = 0
        
        # Determine status emoji
        status_emoji = {
            'NEW': '🟡',
            'PARTIALLY_FILLED': '🔵',
            'FILLED': '✅',
            'CANCELED': '❌',
            'REJECTED': '⚠️',
            'EXPIRED': '⌛'
        }.get(status, '⚪')
        
        response_text = [
            "\n" + "=" * 50,
            "ORDER RESPONSE",
            "=" * 50,
            f"{status_emoji} Status:        {status}",
            f"📝 Order ID:     {order_id}",
            f"📊 Executed Qty: {executed_qty} / {orig_qty} ({fill_pct:.1f}%)"
        ]
        
        if avg_price != '0' and float(avg_price) > 0:
            response_text.append(f"💰 Avg Price:    {avg_price}")
        
        # Add success/failure message
        if status in ['FILLED', 'PARTIALLY_FILLED']:
            response_text.append(f"\n✅ SUCCESS: Order placed successfully")
        elif status == 'NEW':
            response_text.append(f"\n🟡 PENDING: Order accepted and awaiting execution")
        elif status in ['REJECTED', 'EXPIRED', 'CANCELED']:
            reject_reason = response.get('rejectReason', 'Unknown')
            response_text.append(f"\n❌ FAILURE: Order was {status} - {reject_reason}")
        else:
            response_text.append(f"\n❓ UNKNOWN: Order status unknown")
        
        response_text.append("=" * 50)
        
        return "\n".join(response_text)
    
    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Dict:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair symbol
            side: BUY or SELL
            quantity: Order quantity
            
        Returns:
            Order response dictionary
        """
        self.logger.info(f"Placing MARKET order: {side} {quantity} {symbol}")
        
        order_params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'MARKET',
            'quantity': quantity
        }
        
        # Log request summary
        self.logger.info(self.format_order_summary(order_params))
        
        # Place order
        response = self.client.place_order(
            symbol=symbol,
            side=side,
            order_type='MARKET',
            quantity=quantity
        )
        
        # Log response
        self.logger.info(self.format_order_response(response))
        
        return response
    
    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = 'GTC'
    ) -> Dict:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair symbol
            side: BUY or SELL
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (GTC, IOC, FOK)
            
        Returns:
            Order response dictionary
        """
        self.logger.info(f"Placing LIMIT order: {side} {quantity} {symbol} @ {price}")
        
        order_params = {
            'symbol': symbol,
            'side': side.upper(),
            'type': 'LIMIT',
            'quantity': quantity,
            'price': price,
            'timeInForce': time_in_force
        }
        
        # Log request summary
        self.logger.info(self.format_order_summary(order_params))
        
        # Place order
        response = self.client.place_order(
            symbol=symbol,
            side=side,
            order_type='LIMIT',
            quantity=quantity,
            price=price,
            time_in_force=time_in_force
        )
        
        # Log response
        self.logger.info(self.format_order_response(response))
        
        return response