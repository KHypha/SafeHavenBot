from telegram_bot.bot import setup_telegram_bot
from binance_api.binance_client import BinanceFuturesAPI

if __name__ == '__main__':

    #telegram_token = "5844206506:AAH9E0vvUZq_7nRSOU7i0DQnrt7a8zkH_qg"
    telegram_token = "6821901694:AAFgb3P63a_eDLDtbTo3HNqQNvJfkhRqL7g"
    api_key = "YOUR_BINANCE_API_KEY"
    api_secret = "YOUR_BINANCE_API_SECRET"

    # Initialize the Telegram bot
    setup_telegram_bot(telegram_token)

    # Initialize the Binance API client
    binance_api = BinanceFuturesAPI(api_key, api_secret)

