# Binance Futures Trading Bot

## Overview

A Python-based CLI trading bot for Binance Futures Testnet (USDT-M). The application allows users to place BUY and SELL orders using MARKET and LIMIT order types through a clean command-line interface. The project includes input validation, logging, exception handling, and a reusable code structure.

---

## Features

* Place MARKET orders
* Place LIMIT orders
* Support BUY and SELL sides
* Binance Futures Testnet integration
* Command-line interface using argparse
* Input validation
* Structured project architecture
* API request and response logging
* Error handling for invalid input, API errors, and network issues

---

## Project Structure

```text
binance-futures-trading-bot/
│
├── bot/
│   ├── __init__.py
│   ├── client.py
│   ├── orders.py
│   ├── validators.py
│   └── logging_config.py
│
├── logs/
│   ├── market_order.log
│   └── limit_order.log
│
├── cli.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Requirements

* Python 3.10+
* Binance Futures Testnet Account
* Binance Testnet API Key and Secret

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/vt-nanni26/binance-futures-trading-bot.git
cd binance-futures-trading-bot
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the project root:

```env
API_KEY=your_binance_api_key
API_SECRET=your_binance_api_secret
```

Example file:

```env
API_KEY=your_api_key_here
API_SECRET=your_api_secret_here
```

---

## Binance Testnet

Base URL:

```text
https://testnet.binancefuture.com
```

The application connects to Binance Futures Testnet for all order operations.

---

## Usage

### MARKET BUY Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### MARKET SELL Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.001
```

### LIMIT BUY Order

```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000
```

### LIMIT SELL Order

```bash
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 100000
```

---

## Sample Output

```text
Input validation passed

Order details: BUY 0.001 BTCUSDT

Connecting to Binance Futures Testnet...

API client initialized successfully

ORDER REQUEST SUMMARY

Symbol: BTCUSDT
Side: BUY
Type: MARKET
Quantity: 0.001

Order completed successfully!

Order ID: 13802493952
```

---

## Logging

Logs are automatically saved in the `logs/` directory.

Logged information includes:

* API requests
* API responses
* Order details
* Validation errors
* Network errors
* Binance API errors

---

## Error Handling

The application handles:

* Invalid symbols
* Invalid order sides
* Invalid order types
* Missing price for LIMIT orders
* API authentication issues
* Timestamp synchronization issues
* Network failures
* Binance API exceptions

---

## Assumptions

* Binance Futures Testnet account is active.
* API credentials are valid and have Futures permissions.
* User has sufficient testnet balance for order execution.
* Internet connection is available during execution.

---

## Author

Assessment Submission – Python Developer Trading Bot Challenge
