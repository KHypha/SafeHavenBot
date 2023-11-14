from binance.client import Client
import requests

class BinanceFuturesAPI:
    def __init__(self, api_key, api_secret, context):
        self.client = Client(api_key, api_secret, testnet=True)
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

    def cancel_order(self, symbol, order_id):
        try:
            cancelled_order = self.client.futures_cancel_order(symbol=symbol, orderId=order_id)
            return cancelled_order
        except Exception as e:
            print(f"Error cancelling order: {e}")
            return None
    
    def get_klines(self, symbol, interval):
        """Get OHLC (Open/High/Low/Close) data for a symbol and interval."""
        klines = self.client.futures_klines(symbol=symbol, interval=interval, limit=1)
        if klines:
            kline = klines[0]
            open_price = float(kline[1])
            high_price = float(kline[2])
            low_price = float(kline[3])
            close_price = float(kline[4])
            return open_price, high_price, low_price, close_price
        else:
            return None

    def display_orders(self):
        try:
            # Get open orders
            orders = self.client.futures_get_open_orders()
            return orders
        except Exception as e:
            print(f"Error fetching open orders: {e}")
            return None
    
    def get_top_movers(self):
        # Define the endpoint URL
        url = 'https://fapi.binance.com/fapi/v1/ticker/24hr'

        # Make a GET request to fetch the 24-hour ticker data for all trading pairs
        response = requests.get(url)
        data = response.json()

        # Filter the data to get only USD-M futures pairs
        usd_m_futures_pairs = [pair for pair in data if pair['symbol'].endswith('USDT')]
        
        # Sort the pairs by their price change percentage (gainers and losers)
        top_gainers = sorted(usd_m_futures_pairs, key=lambda x: float(x['priceChangePercent']), reverse=True)[:10]
        top_losers = sorted(usd_m_futures_pairs, key=lambda x: float(x['priceChangePercent']))[:10]

        return top_gainers, top_losers
    def get_mark_price(self, symbol):
        # Use the Binance API to fetch the mark price for the given symbol
        mark_price_info = self.client.futures_mark_price(symbol=symbol)
        mark_price = mark_price_info["markPrice"]
        return mark_price

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
