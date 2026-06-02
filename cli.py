#!/usr/bin/env python3
"""
Command-line interface for Binance Futures Trading Bot
"""

import sys
import argparse
from typing import Optional

# Try to import colorama for colored output
try:
    from colorama import init, Fore, Style
    init()  # Initialize colorama for Windows support
    HAS_COLOR = True
except ImportError:
    HAS_COLOR = False
    # Define dummy color constants
    class Fore:
        RED = GREEN = YELLOW = CYAN = RESET = ''
    class Style:
        BRIGHT = DIM = RESET_ALL = ''

from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import OrderValidator
from bot.logging_config import setup_logging


def colorize(text: str, color: str = Fore.RESET, bright: bool = False) -> str:
    """
    Add color to text if colorama is available.
    
    Args:
        text: Text to colorize
        color: Color constant from Fore
        bright: Whether to use bright style
        
    Returns:
        Colorized text or original text if color not available
    """
    if HAS_COLOR:
        style = Style.BRIGHT if bright else ''
        return f"{style}{color}{text}{Style.RESET_ALL}"
    return text


def print_error(message: str):
    """Print error message in red."""
    print(colorize(f"❌ Error: {message}", Fore.RED, bright=True), file=sys.stderr)


def print_success(message: str):
    """Print success message in green."""
    print(colorize(f"✅ {message}", Fore.GREEN, bright=True))


def print_info(message: str):
    """Print info message in cyan."""
    print(colorize(f"ℹ️  {message}", Fore.CYAN))


def print_warning(message: str):
    """Print warning message in yellow."""
    print(colorize(f"⚠️  {message}", Fore.YELLOW))


def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments object
    """
    parser = argparse.ArgumentParser(
        description='Binance Futures Trading Bot - Place orders on Binance Futures Testnet',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Market Order (BUY):
    python cli.py -s BTCUSDT -b BUY -t MARKET -q 0.001
  
  Market Order (SELL):
    python cli.py -s ETHUSDT -b SELL -t MARKET -q 0.01
  
  Limit Order (BUY):
    python cli.py -s BTCUSDT -b BUY -t LIMIT -q 0.001 -p 50000
  
  Limit Order (SELL):
    python cli.py -s ETHUSDT -b SELL -t LIMIT -q 0.01 -p 3000

Note: All orders are placed on Binance Futures TESTNET.
        """
    )
    
    parser.add_argument(
        '-s', '--symbol',
        type=str,
        required=True,
        help='Trading pair symbol (e.g., BTCUSDT, ETHUSDT)'
    )
    
    parser.add_argument(
        '-b', '--side',
        type=str,
        required=True,
        choices=['BUY', 'SELL'],
        help='Order side: BUY or SELL'
    )
    
    parser.add_argument(
        '-t', '--type',
        type=str,
        required=True,
        choices=['MARKET', 'LIMIT'],
        help='Order type: MARKET or LIMIT'
    )
    
    parser.add_argument(
        '-q', '--quantity',
        type=float,
        required=True,
        help='Order quantity (e.g., 0.001 for BTC)'
    )
    
    parser.add_argument(
        '-p', '--price',
        type=float,
        help='Price for LIMIT orders (required if order type is LIMIT)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Custom log file path (optional)'
    )
    
    return parser.parse_args()


def main():
    """Main entry point for the CLI application."""
    
    # Print banner
    print(colorize("=" * 60, Fore.CYAN, bright=True))
    print(colorize("🤖 Binance Futures Trading Bot - Testnet", Fore.CYAN, bright=True))
    print(colorize("=" * 60, Fore.CYAN, bright=True))
    print()
    
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.log_file)
    
    # Validate inputs
    is_valid, errors = OrderValidator.validate_all(
        symbol=args.symbol,
        side=args.side,
        order_type=args.type,
        quantity=args.quantity,
        price=args.price
    )
    
    if not is_valid:
        print_error("Input validation failed:")
        for error in errors:
            print(f"  • {error}")
        logger.error(f"Validation failed: {', '.join(errors)}")
        sys.exit(1)
    
    print_success("Input validation passed")
    print_info(f"Order details: {args.side} {args.quantity} {args.symbol}")
    if args.type == 'LIMIT':
        print_info(f"Limit price: {args.price}")
    print()
    
    try:
        # Initialize API client
        print_info("Connecting to Binance Futures Testnet...")
        client = BinanceFuturesClient()
        print_success("API client initialized successfully")
        
        # Initialize order manager
        order_manager = OrderManager(client)
        
        # Place order based on type
        if args.type == 'MARKET':
            logger.info(f"Placing MARKET order: {args.side} {args.quantity} {args.symbol}")
            response = order_manager.place_market_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity
            )
        else:  # LIMIT order
            if not args.price:
                print_error("Price is required for LIMIT orders")
                sys.exit(1)
            
            logger.info(f"Placing LIMIT order: {args.side} {args.quantity} {args.symbol} @ {args.price}")
            response = order_manager.place_limit_order(
                symbol=args.symbol,
                side=args.side,
                quantity=args.quantity,
                price=args.price
            )
        
        # Check final status
        if response.get('status') in ['FILLED', 'PARTIALLY_FILLED', 'NEW']:
            print()
            print_success("Order completed successfully!")
            
            # Show additional info
            if response.get('orderId'):
                print_info(f"Order ID: {response['orderId']}")
            
            # Suggest checking position if BUY order
            if args.side == 'BUY' and response.get('executedQty', '0') != '0':
                print_info("Position opened. Use Binance Futures interface to manage.")
            
        else:
            print_warning("Order was not fully executed. Check logs for details.")
            
        # Log completion
        logger.info("Order processing completed")
        
    except ValueError as e:
        print_error(f"Configuration error: {str(e)}")
        logger.error(f"Configuration error: {str(e)}")
        print_info("Please check your .env file and ensure API keys are set correctly")
        sys.exit(1)
        
    except Exception as e:
        print_error(f"Failed to place order: {str(e)}")
        logger.error(f"Order failed: {str(e)}", exc_info=True)
        
        # Provide helpful suggestions based on error
        error_msg = str(e).lower()
        if "insufficient balance" in error_msg:
            print_info("Suggestion: Check your testnet balance in the Futures wallet")
        elif "invalid symbol" in error_msg:
            print_info("Suggestion: Verify the symbol is correct and active on Binance Futures")
        elif "network" in error_msg or "timeout" in error_msg:
            print_info("Suggestion: Check your internet connection and try again")
        
        sys.exit(1)
    
    finally:
        print()
        print(colorize("=" * 60, Fore.CYAN, bright=True))
        print_info(f"Logs have been saved to: {args.log_file or 'logs/ directory'}")
        print(colorize("=" * 60, Fore.CYAN, bright=True))


if __name__ == "__main__":
    main()