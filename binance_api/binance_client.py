from binance.client import Client
import requests

class BinanceFuturesAPI:
    def __init__(self, api_key, api_secret, context):
        self.client = Client(api_key, api_secret)
        self.context = context
    def check_hedge_mode(self):
         # Check if hedge mode is activated
        position_mode = self.client.futures_get_position_mode()
        hedge_mode = position_mode['dualSidePosition']
        return hedge_mode

    def get_symbol_price(self, symbol):
        """Get the current price of a symbol."""
        ticker = self.client.get_symbol_ticker(symbol=symbol)
        if ticker:
            return float(ticker['price'])
        else:
            return None

    def get_klines(self, symbol, interval):
        """Get OHLC (Open/High/Low/Close) data for a symbol and interval."""
        klines = self.client.get_klines(symbol=symbol, interval=interval)
        if klines:
            # Format the klines data
            formatted_data = "\n".join([f"Open time: {kline[0]}, Open: {kline[1]}, High: {kline[2]}, Low: {kline[3]}, Close: {kline[4]}" for kline in klines])
            return formatted_data
        else:
            return None

    def get_top_gainers(self):
        """Get the top gainers."""
        try:
            response = requests.get('https://api.binance.com/api/v3/ticker/24hr')
            tickers = response.json()
            tickers_sorted = sorted(tickers, key=lambda x: float(x['priceChangePercent']), reverse=True)
            top_gainers = "\n".join([f"Symbol: {ticker['symbol']}, Change Percent: {ticker['priceChangePercent']}%" for ticker in tickers_sorted[:5]])
            return top_gainers
        except Exception as e:
            print(f"Error fetching top gainers: {e}")
            return None

    def get_top_losers(self):
        """Get the top losers."""
        try:
            response = requests.get('https://api.binance.com/api/v3/ticker/24hr')
            tickers = response.json()
            tickers_sorted = sorted(tickers, key=lambda x: float(x['priceChangePercent']))
            top_losers = "\n".join([f"Symbol: {ticker['symbol']}, Change Percent: {ticker['priceChangePercent']}%" for ticker in tickers_sorted[:5]])
            return top_losers
        except Exception as e:
            print(f"Error fetching top losers: {e}")
            return None
    def check_balances(self):
        account_info = self.client.futures_account()
        return account_info
    
    def get_position_quantity(self):
        symbol = self.context.user_data.get('symbol')
        position_mode = self.client.futures_get_position_mode()
        hedge_mode = position_mode['dualSidePosition']

        if not symbol:
            return None

        # Get open positions
        open_positions = self.client.futures_position_information()

        # Find the open position for the specified symbol and position side
        for position in open_positions:
            if hedge_mode:
                position_side = self.context.user_data.get('position_side')
                if position['symbol'] == symbol and position['positionSide'] == position_side:
                    return position['positionAmt']
            else:
                if position['symbol'] == symbol:
                    return position['positionAmt']

        return None
    
    def place_limit_order(self):
        return self._place_order(Client.ORDER_TYPE_LIMIT)

    def place_market_order(self):
        return self._place_order(Client.ORDER_TYPE_MARKET)

    def place_stop_limit_order(self):
        return self._place_order(Client.ORDER_TYPE_STOP_MARKET)

    def place_take_profit_order(self):
        return self._place_order(Client.FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET)

    def place_stop_loss_order(self):
        return self._place_order(Client.FUTURE_ORDER_TYPE_STOP_MARKET)

    def _place_order(self, order_type):
        # Accessing user_data from context
        user_data = self.context.user_data

        # Extract required parameters from user_data
        symbol = user_data.get('symbol')
        quantity = user_data.get('quantity')
        side = user_data.get('side')
        stop_price = user_data.get('stop_price')
        position_side = user_data.get('position_side')

        # Check if hedge mode is activated
        position_mode = self.client.futures_get_position_mode()
        hedge_mode = position_mode['dualSidePosition']

        # Additional checks or adjustments based on order_type

        order_params = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'type': order_type,
        }

        if hedge_mode:
            order_params['positionSide'] = position_side

        if order_type == Client.ORDER_TYPE_LIMIT:
            order_params.update({
                'timeInForce': Client.TIME_IN_FORCE_GTC,
                'price': user_data.get('price')
            })

        if order_type == Client.FUTURE_ORDER_TYPE_TAKE_PROFIT_MARKET:
            order_params.update({
                'stopPrice': stop_price,
                'timeInForce': Client.TIME_IN_FORCE_GTC,
            })

        if order_type == Client.FUTURE_ORDER_TYPE_STOP_MARKET:
            order_params.update({
                'stopPrice': stop_price,
                'timeInForce': Client.TIME_IN_FORCE_GTC,
            })

        # Place the order using extracted parameters
        order = self.client.futures_create_order(**order_params)
        return order