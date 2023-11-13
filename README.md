# SafeHavenBot
# Telegram Binance Trading Bot

## Overview

This project is a Telegram-based trading bot that integrates with the Binance API, allowing users to execute trading orders, check balances, and manage their portfolio seamlessly through Telegram.

## Features

- **User-Friendly Interface:** Interact with the bot using simple commands and buttons for a smooth user experience.

- **Secure API Integration:** Safely connect to the Binance API with secure credential storage and communication.

- **Advanced Risk Management:** Tailor risk parameters for each trade, ensuring responsible and secure trading practices.

- **Comprehensive Help System:** Access a detailed help system for guidance on available commands and how to use them.

## Getting Started

### Prerequisites

- Python 3.x
- Telegram account
- Binance account with API access

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/KHypha/SafeHavenBot.git

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   
3. Set up your Telegram Bot and Binance API credentials as described in Configuration.

Configuration
Create a Telegram Bot on BotFather and note down the token.

Configure your Binance API credentials:

Create an API key in your Binance account.
Save the API key and secret securely.
Create a config.ini file in the root directory with the following structure:

   ```ini
   [Telegram]
   token = YOUR_TELEGRAM_BOT_TOKEN
   [Binance]
   api_key = YOUR_BINANCE_API_KEY
   api_secret = YOUR_BINANCE_API_SECRET
```


4. Usage
Run the bot:

   ```bash
   python main.py

Start interacting with the bot on Telegram using the provided commands.

Contributing
Contributions are welcome! Please follow the contribution guidelines.

License
This project is licensed under the MIT License.
