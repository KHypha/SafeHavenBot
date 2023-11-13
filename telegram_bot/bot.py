import telegram
import sqlite3
from telegram import ParseMode, ReplyKeyboardMarkup, KeyboardButton

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,ConversationHandler
from binance_api.binance_client import BinanceFuturesAPI
from telegram import Update, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup , ReplyKeyboardRemove
 

# Define conversation states
SELECT_ORDER_TYPE, ENTER_SYMBOL, ENTER_SIDE, ENTER_POSITION_SIDE, ENTER_QUANTITY, ENTER_PRICE, ENTER_STOP_PRICE, ENTER_LIMIT_PRICE = range(8)

ENTER_RISK_PERCENTAGE, ENTER_MAX_LOSSES, ENTER_MAX_LEVERAGE, ENTER_DAILY_PROFIT_TARGET, ENTER_ACCOUNT_BALANCE_RISK = range(5)

# Constants for order types
MARKET_LONG = 'long'
MARKET_SHORT = 'short'
LIMIT_ORDER = 'limit'
STOP_LIMIT_ORDER = 'stoplimit'
STOP_LOSS_ORDER = 'stoploss'
TAKE_PROFIT_ORDER = 'takeprofit'

DATABASE_FILE = 'credentials.db'


from telegram.ext import CommandHandler, MessageHandler, Filters

# ... Your existing code ...

# Define a function to handle both the command and its emoji-enhanced version
def set_commands(update, context):
    command_text = update.message.text.lower()

    # Check if the command or its emoji-enhanced version is received
    if command_text in ['/setapi', '⚙️ set api']:
        set_api(update, context)
    elif command_text in ['/balances', '💰 balances']:
        check_balances(update, context)
    elif command_text in ['/order', '📈 open order']:
        start_order(update, context)
    elif command_text in ['/cancel', '🚫 cancel']:
        cancel(update, context)
    elif command_text in ['/check_price', '💹 check price']:
        check_price(update, context)
    elif command_text in ['/get_ohlc', '📊 get ohlc']:
        get_ohlc(update, context)
    elif command_text in ['/top_gainers', '🔝 top gainers']:
        view_top_gainers(update, context)
    elif command_text in ['/top_losers', '🔙 top losers']:
        view_top_losers(update, context)
    elif command_text in ['/setrisk', '🔄 set risk']:
        set_risk(update, context)
    elif command_text in ['/help', '❓ help']:
        help_command(update, context)
    else:
        # Handle other cases or provide a response for unrecognized input
        update.message.reply_text("Unrecognized command. Please use /start for available commands")

# Create the CommandHandler for the emoji-enhanced version
set_commands_handler = MessageHandler(Filters.text & ~Filters.command, set_commands)


# Initialize the Telegram bot
from telegram import ParseMode, ReplyKeyboardMarkup, KeyboardButton

# Modify your existing start function to include a simple dashboard
def start(update, context):
    start_message = ("Welcome to the Binance Futures bot! You can use the following commands:\n"
                     "⚙️ **Set API** - Set up your Binance API credentials\n"
                     "💰 **Balances** - Check your account balances\n"
                     "📈 **Open Order** - Open a new order\n"
                     "🚫 **Cancel** - Cancel the current operation\n"
                     "💹 **Check Price** - Check the current price of a symbol\n"
                     "📊 **Get OHLC** - Get OHLC data for a symbol\n"
                     "🔝 **Top Gainers** - View top gainers\n"
                     "🔙 **Top Losers** - View top losers\n"
                     "🔄 **Set Risk** - Set up your risk parameters\n"
                     "❓ **Help** - Show help message")

    keyboard = [
            [KeyboardButton("⚙️ Set API") , KeyboardButton("🔄 Set Risk"), KeyboardButton("💰 Balances")],
            [KeyboardButton("💹 Check Price"), KeyboardButton("📊 Get OHLC"), KeyboardButton("📈 Open Order")],
            [KeyboardButton("🔝 Top Gainers"), KeyboardButton("🔙 Top Losers"), KeyboardButton("❓ Help")],
            
        ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)

    risk_params = get_risk_params(user_id)

    if risk_params:
        risk_message = f"\n\nWelcome back! Your risk parameters are set as follows:"
        risk_message += f"\n- Maximum Risk Percentage: {risk_params['max_risk_percentage']}%"
        risk_message += f"\n- Maximum Losses Per Day: {risk_params['max_losses_per_day']}"
        risk_message += f"\n- Maximum Leverage: {risk_params['max_leverage']}"
        risk_message += f"\n- Daily Profit Target: {risk_params['daily_profit_target']} USDT"

        update.message.reply_text(f"{risk_message}\n{start_message}", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    else:
        update.message.reply_text(f"{start_message}", reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END  # End the conversation

def set_risk(update, context):
    update.message.reply_text("Let's set up your risk parameters.\n"
                              "Please enter your maximum risk percentage per trade (e.g., 1.5 for 1.5%):")
    return ENTER_RISK_PERCENTAGE

def help_command(update, context):
    help_text = (
        "Here are the available commands:\n"
        "/start - Start the bot.\n"
        "/setapi or ⚙️set api - Set up your Binance API credentials.\n"
        "/balances or 💰balances - Check your account balances.\n"
        "/openlong - Open a long market order.\n"
        "/openshort - Open a short market order.\n"
        "/open_order or 📈Open Order - Open a new order.\n"
        "/cancel - Cancel the current operation.\n"
        "/check_price - Check the current price of a symbol.\n"
        "/get_ohlc - Get OHLC data for a symbol.\n"
        "/top_gainers - View top gainers.\n"
        "/top_losers - View top losers.\n"
        "/setrisk - Set up your risk parameters.\n"
        "/clearrisk - Clear your risk parameters.\n"
        "/clearapi - Clear your API credentials.\n"
        "/help - Get information on available commands and their usage."
    )
    update.message.reply_text(help_text)

def receive_max_risk_percentage(update, context):
    try:
        max_risk_percentage = float(update.message.text.strip())
        context.user_data['max_risk_percentage'] = max_risk_percentage

        # Prompt for the next parameter
        update.message.reply_text("Please enter the maximum number of losses per day:")
        return ENTER_MAX_LOSSES

    except ValueError:
        update.message.reply_text("Invalid input. Please enter a valid number.")

def receive_max_losses_per_day(update, context):
    try:
        max_losses_per_day = int(update.message.text.strip())
        context.user_data['max_losses_per_day'] = max_losses_per_day

        # Prompt for the next parameter
        update.message.reply_text("Please enter the maximum leverage:")
        return ENTER_MAX_LEVERAGE

    except ValueError:
        update.message.reply_text("Invalid input. Please enter a valid number.")

def receive_max_leverage(update, context):
    try:
        max_leverage = int(update.message.text.strip())
        context.user_data['max_leverage'] = max_leverage

        # Prompt for the next parameter
        update.message.reply_text("Please enter the daily profit target:")
        return ENTER_DAILY_PROFIT_TARGET

    except ValueError:
        update.message.reply_text("Invalid input. Please enter a valid number.")

def receive_daily_profit_target(update, context):
    try:
        daily_profit_target = float(update.message.text.strip())
        context.user_data['daily_profit_target'] = daily_profit_target

        # Save risk management parameters in the database
        user_id = update.message.from_user.id
        save_risk_params(user_id, context.user_data)

        update.message.reply_text("Risk management parameters have been saved.")
        return ConversationHandler.END

    except ValueError:
        update.message.reply_text("Invalid input. Please enter a valid number.")

def save_risk_params(user_id, risk_params):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO risk_management (user_id, max_risk_percentage, max_losses_per_day, max_leverage, daily_profit_target) VALUES (?, ?, ?, ?, ?)',
                   (user_id, risk_params['max_risk_percentage'], risk_params['max_losses_per_day'], risk_params['max_leverage'], risk_params['daily_profit_target']))
    conn.commit()
    conn.close()

def get_risk_params(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    # Execute a SELECT query to get the risk parameters for the given user_id
    cursor.execute("SELECT max_risk_percentage, max_losses_per_day, max_leverage, daily_profit_target FROM risk_management WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    # Close the database connection
    conn.close()

    # If result is not None, return a dictionary with risk parameters
    if result:
        max_risk_percentage, max_losses_per_day, max_leverage, daily_profit_target = result
        return {
            'max_risk_percentage': max_risk_percentage,
            'max_losses_per_day': max_losses_per_day,
            'max_leverage': max_leverage,
            'daily_profit_target': daily_profit_target,
        }
    else:
        # If no result, return None
        return None

def set_api(update, context):
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)
    reply_markup = ReplyKeyboardMarkup([[KeyboardButton('/cancel')]], one_time_keyboard=True)

    update.message.reply_text("Let's set up your Binance API credentials.\n"
                              f"Currently set to \n API Key: {api_key}"
                              f"\nAPI Secret: {api_secret}"
                              "\nPlease enter your API Key:", reply_markup=reply_markup)

    return ENTER_API_KEY
ENTER_API_KEY, ENTER_API_SECRET = range(2)

def get_api_key(update, context):
    api_key = update.message.text.strip()
    context.user_data['api_key'] = api_key
    update.message.reply_text("API Key saved. Now, please enter your API secret:")
    return ENTER_API_SECRET

def get_api_secret(update, context):
    api_secret = update.message.text.strip()
    context.user_data['api_secret'] = api_secret

    # Save the credentials securely in the database or your preferred storage
    save_credentials(update.message.from_user.id, context.user_data['api_key'], context.user_data['api_secret'])

    update.message.reply_text("API credentials have been saved. You can now use the bot to interact with Binance.")
    return ConversationHandler.END  # End the conversation

def save_credentials(user_id, api_key, api_secret):
    conn = sqlite3.connect('credentials.db')
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO user_credentials (user_id, api_key, api_secret) VALUES (?, ?, ?)', (user_id, api_key, api_secret))
    conn.commit()
    conn.close()

# Define a function to get user credentials from the database
def get_credentials(user_id):
    conn = sqlite3.connect('credentials.db')
    cursor = conn.cursor()
    cursor.execute("SELECT api_key, api_secret FROM user_credentials WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        api_key, api_secret = result
        return api_key, api_secret
    else:
        return None, None

def get_binance_api(update, context):
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)

    if api_key and api_secret:
        return BinanceFuturesAPI(api_key, api_secret, context)
    else:
        update.message.reply_text("API credentials not found. Please set up your credentials using /start.")
        return None  # Return None if credentials are not found

def check_price(update, context):
    user_input = context.args

    if len(user_input) != 1:
        message = "Usage: /check_price <symbol>"
        message += "\n/check_price BTCUSDT"
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
        return

    symbol = user_input[0].upper()  # Assuming the user enters the symbol in uppercase

    binance_api = get_binance_api(update, context)
    price = binance_api.get_symbol_price(symbol)

    if price:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Current price of {symbol}: {price}")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Symbol {symbol} not found or invalid.")
  
def get_ohlc(update, context):
    user_input = context.args

    if len(user_input) != 2:
        message = "Usage: /get_ohlc <symbol> <interval>"
        message += "\n/get_ohlc BTCUSDT 1h"
        context.bot.send_message(chat_id=update.message.chat_id, text=message)
        return

    symbol = user_input[0].upper()  # Assuming the user enters the symbol in uppercase
    interval = user_input[1].lower()  # Assuming the user enters the interval in lowercase

    binance_api = get_binance_api(update, context)
    ohlc_data = binance_api.get_klines(symbol, interval)

    if ohlc_data:
        # Process and format the OHLC data as needed
        # Then send it as a message to the user
        context.bot.send_message(chat_id=update.message.chat_id, text=f"OHLC data for {symbol} ({interval}):\n{ohlc_data}")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Symbol {symbol} or interval {interval} not found or invalid.")
  
def view_top_gainers(update, context):
    binance_api = get_binance_api(update, context)
    top_gainers = binance_api.get_top_gainers()

    if top_gainers:
        # Process and format the top gainers data as needed
        # Then send it as a message to the user
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Top Gainers:\n{top_gainers}")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Failed to fetch top gainers.")
 
def view_top_losers(update, context):
    binance_api = get_binance_api(update, context)
    top_losers = binance_api.get_top_losers()

    if top_losers:
        # Process and format the top losers data as needed
        # Then send it as a message to the user
        context.bot.send_message(chat_id=update.message.chat_id, text=f"Top Losers:\n{top_losers}")
    else:
        context.bot.send_message(chat_id=update.message.chat_id, text="Failed to fetch top losers.")
 
def check_balances(update, context):
    binance_api = get_binance_api(update, context)
    account_info = binance_api.check_balances()
    balances = account_info['assets']

    # Process the 'account_info' and format it as a response to the user
    response_text = "Your account balances:\n"
    unrealized_pnl = float(account_info["totalUnrealizedProfit"])

    total_balance = sum(float(balance['walletBalance']) for balance in balances) + unrealized_pnl

    for balance in balances:
            if float(balance['walletBalance']) > 0.0:
                response_text += f"💳 {balance['asset']}: 💲{float(balance['walletBalance']):.4f}\n"
    update.message.reply_text(response_text)
 
def open_long(update, context):
    chat_id = update.message.chat_id
    
    binance_api = get_binance_api(update, context)


    try:
            user_input = context.args

            if len(user_input) != 2:
                message = "Usage: /long <symbol> <quantity>"
                message += "\n/long LTCUSDT 1"
                context.bot.send_message(chat_id=chat_id, text=message)
                return

            symbol = user_input[0]
            quantity = float(user_input[1])
            position_side = "LONG"  # Set position side to SHORT
            side = "BUY"
            order = binance_api.place_market_order(symbol, side, position_side, quantity,)

            update.message.reply_text(f"Market order placed:\n{order}")
    except Exception as e:
            update.message.reply_text(f"An error occurred: {str(e)}")

   
def display_orders(update, context):
    chat_id = update.message.chat_id
    
    binance_api = get_binance_api(update, context)
    
    try:
        orders = binance_api.display_orders()
        
        if not orders:
            context.bot.send_message(chat_id=chat_id, text="No open orders found.")
            return
        
        orders_text = "Open orders:\n"
        for order in orders:
            orders_text += f"Symbol: {order['symbol']}, Side: {order['side']}, Quantity: {order['origQty']}, Price: {order['price']}\n"
        
        context.bot.send_message(chat_id=chat_id, text=orders_text)
    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=f"An error occurred: {e}")

def cancel_order(update, context):
    chat_id = update.message.chat_id
    
    binance_api = get_binance_api(update, context)
    
    try:
        orders = binance_api.display_orders()
        
        if not orders:
            context.bot.send_message(chat_id=chat_id, text="No open orders found.")
            return
    
        keyboard = []
        for order in orders:
            order_details = f"{order['side']} {order['origQty']} {order['symbol']} @ {order['price']}"
            callback_data = f"cancel__{order['symbol']}__{order['orderId']}"  # Include symbol and order ID in callback data
            keyboard.append([InlineKeyboardButton(order_details, callback_data=callback_data)])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.send_message(chat_id=chat_id, text="Select orders to cancel:", reply_markup=reply_markup)
        
    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=f"An error occurred: {e}")

def open_short(update, context):
    chat_id = update.message.chat_id
    
    binance_api = get_binance_api(update, context)


    try:
            user_input = context.args

            if len(user_input) != 2:
                message = "Usage: /short <symbol> <quantity>"
                message += "\n/short LTCUSDT 1"
                context.bot.send_message(chat_id=chat_id, text=message)
                return

            symbol = user_input[0]
            quantity = float(user_input[1])
            position_side = "SHORT"  # Set position side to SHORT
            side = "SELL"
            order = binance_api.place_market_order(symbol, side, position_side, quantity,)

            update.message.reply_text(f"Market order placed:\n{order}")
    except Exception as e:
            update.message.reply_text(f"An error occurred: {str(e)}")

    else:
        update.message.reply_text("API credentials not found. Please set up your credentials using /start.")

def open_limit_order(update, context):
    chat_id = update.message.chat_id
    
    binance_api = get_binance_api(update, context)

        # Parse user input to get order parameters
    try:
        user_input = context.args

        if len(user_input) <= 3:
            context.bot.send_message(chat_id=chat_id, text="Usage: /limit_order <symbol> <quantity> <side> <price> [positionSide]\n"
                                    "/limit_order LTCUSDT 2 BUY 66.15 LONG\n"
                                    "/limit_order  LTCUSDT 2 SELL 66.5 LONG\n"
                                    "/limit_order  LTCUSDT 2 BUY 66.15 SHORT\n"
                                    "/limit_order  LTCUSDT 2 SELL 66.5 SHORT")
            return

        symbol = user_input[0]
        quantity = float(user_input[1])
        side = user_input[2].upper()  # 'BUY' or 'SELL'
        price = float(user_input[3])
        position_side = user_input[4].upper() if len(user_input) > 4 else None  # Optional 'LONG' or 'SHORT'

        # If positionSide is not provided, use 'BUY' for long and 'SELL' for short
        if position_side is None:
            position_side = 'LONG' if side == 'BUY' else 'SHORT'
        order = binance_api.place_limit_order(symbol, side, position_side, quantity, price)
        update.message.reply_text(f"Limit order placed:\n{order}")
    except Exception as e:
        update.message.reply_text(f"An error occurred: {str(e)}")

    else:
        update.message.reply_text("API credentials not found. Please set up your credentials using /start.")
 
def start_order(update, context):
    context.user_data.clear()  # Clear any previous user data
    
    # Updated reply keyboard markup
    reply_keyboard = [
        [ 'Long Market','Short Market'],
        ['Limit Order','Stop-Limit Order', ],
        ['Take-Profit Order', 'Stop-Loss Order']
    ]
    
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

    update.message.reply_text("Let's start opening an order. Please choose the order type:", reply_markup=reply_markup)
    return SELECT_ORDER_TYPE

def select_order_type(update, context):
    side_keyboard = [
        [ 'BUY','SELL'],
        ['/cancel', ],
        
    ]
    reply_markup = ReplyKeyboardMarkup(side_keyboard, one_time_keyboard=True)
    user_input = update.message.text.lower().split()[0]
    context.user_data['order_type'] = user_input
    if user_input == MARKET_LONG:
        context.user_data['side'] = 'BUY'
        update.message.reply_text("Please enter the symbol for the order:")
        return ENTER_SYMBOL   

    elif user_input == MARKET_SHORT:
        context.user_data['side'] = 'SELL'
        update.message.reply_text("Please enter the symbol for the order:")
        return ENTER_SYMBOL
    else:
        update.message.reply_text("Please enter the side for the order:",reply_markup=reply_markup)
        return ENTER_SIDE

def get_side(update, context):
    side = update.message.text
    context.user_data['side'] = side
    
    binance_api = get_binance_api(update, context)
    hedge_mode = binance_api.check_hedge_mode()
    order_type = context.user_data.get('order_type')
    if hedge_mode :
        if order_type == 'TAKE_PROFIT_ORDER':
            context.user_data['position_side'] = 'LONG' if side =='BUY' else 'SHORT'
        elif order_type == STOP_LOSS_ORDER:
            context.user_data['position_side'] = 'LONG' if side =='SELL' else 'SHORT'
        else:
            update.message.reply_text("Please enter the Position Side (LONG or SHORT):")
            return ENTER_POSITION_SIDE
    
    update.message.reply_text("Please enter the symbol for the order:")
    return ENTER_SYMBOL 
    
  
def get_position_side(update, context):
    position_side = update.message.text.upper()
    if position_side in ['LONG', 'SHORT']:
        context.user_data['position_side'] = position_side
        update.message.reply_text("Please enter the symbol for the order:")
        return ENTER_SYMBOL
    else:
        update.message.reply_text("Invalid position side. Please enter 'LONG' or 'SHORT':")
        return ENTER_POSITION_SIDE
    
def get_symbol(update, context):
    symbol = update.message.text
    context.user_data['symbol'] = symbol

    # Determine the order type based on the context
    order_type = context.user_data.get('order_type')

    if order_type in [MARKET_LONG, MARKET_SHORT, LIMIT_ORDER, STOP_LIMIT_ORDER]:
        update.message.reply_text("Please enter the quantity for the order:")
        return ENTER_QUANTITY  # Proceed to quantity
    elif order_type in [STOP_LOSS_ORDER, 'TAKE_PROFIT_ORDER']:
        update.message.reply_text("Please enter the price for the order:")
        return ENTER_STOP_PRICE  # Proceed to price
    else:
        update.message.reply_text("Invalid order type. Please enter the order type again")
        return SELECT_ORDER_TYPE
    
def get_quantity(update, context):
    quantity = update.message.text
    context.user_data['quantity'] = quantity

    # Determine the order type based on the context
    order_type = context.user_data.get('order_type')

    if order_type == MARKET_LONG or order_type == MARKET_SHORT:
        # For market_long, place a market order with buy side (LONG)
        place_order(update, context)

    elif order_type == LIMIT_ORDER or  order_type == STOP_LIMIT_ORDER:
        # For limit order, proceed to collecting price
        # proceed to collecting stop and limit prices
        update.message.reply_text("Please enter the limit price:")
        return ENTER_LIMIT_PRICE

    return ConversationHandler.END

def get_limit_price(update, context):
    limit_price = update.message.text
    context.user_data['limit_price'] = limit_price
    # Determine the order type and additional parameters based on the context
    order_type = context.user_data.get('order_type')

    # For stop_limit order, place the order\
    if order_type == LIMIT_ORDER:
        place_order(update, context)
    elif order_type == STOP_LIMIT_ORDER:
        update.message.reply_text("Please enter the stop price:")
        return ENTER_STOP_PRICE

    return ConversationHandler.END

   
def get_stop_price(update, context):
    stop_price = update.message.text
    context.user_data['stop_price'] = stop_price
    order_type = context.user_data.get('order_type')
    
    binance_api = get_binance_api(update, context)
    if order_type in [STOP_LOSS_ORDER, 'TAKE_PROFIT_ORDER']:
        #get and assign qty
        quantity = binance_api.get_position_quantity
        context.user_data['quantity'] = quantity

    place_order(update, context)


def place_order(update, context): 
    binance_api = get_binance_api(update, context)
    if binance_api:
        try:
            order_type = context.user_data.get('order_type')
            
            if order_type == MARKET_LONG:
                order = binance_api.place_market_order()
            elif order_type == MARKET_SHORT:
                order = binance_api.place_market_order()
            elif order_type == LIMIT_ORDER:
                order = binance_api.place_limit_order()
            elif order_type == STOP_LIMIT_ORDER:
                order = binance_api.place_stop_limit_order()
            elif order_type == STOP_LOSS_ORDER:
                order = binance_api.place_stop_loss_order()

            elif order_type == 'TAKE_PROFIT_ORDER':
                order = binance_api.place_take_profit_order()

            context.user_data.clear()  # Clear user data

            update.message.reply_text(f"Order placed:\n{order}")
        except Exception as e:
            update.message.reply_text(f"An error occurred: {str(e)}")

    
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Operation canceled.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

def clear_risk_params(update, context):
    user_id = update.message.from_user.id
    clear_risk_params_db(user_id)
    update.message.reply_text("Your risk parameters have been cleared.")

def clear_api_credentials(update, context):
    user_id = update.message.from_user.id
    clear_api_credentials_db(user_id)
    update.message.reply_text("Your API credentials have been cleared.")

def clear_risk_params_db(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM risk_management WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

def clear_api_credentials_db(user_id):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_credentials WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
# Handler to cancel the API setting conversation
def cancel_set_api(update, context):
    update.message.reply_text("API setting canceled.")
    return ConversationHandler.END  # End the conversation

# Create the ConversationHandler for setting API credentials
set_api_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('setapi', set_api)],
    states={
        ENTER_API_KEY: [MessageHandler(Filters.text & ~Filters.command, get_api_key)],
        ENTER_API_SECRET: [MessageHandler(Filters.text & ~Filters.command, get_api_secret)],
    },
    fallbacks=[CommandHandler('cancel', cancel_set_api)]
)
# Create a conversation handler for the order placement process
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('order', start_order)],
    states={
        SELECT_ORDER_TYPE: [MessageHandler(Filters.text & ~Filters.command, select_order_type)],
        ENTER_SYMBOL: [MessageHandler(Filters.text & ~Filters.command, get_symbol)],
        ENTER_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, get_quantity)],
        ENTER_SIDE: [MessageHandler(Filters.text & ~Filters.command, get_side)],
        ENTER_STOP_PRICE: [MessageHandler(Filters.text & ~Filters.command, get_stop_price)],
        ENTER_LIMIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, get_limit_price)],
        ENTER_POSITION_SIDE: [MessageHandler(Filters.text & ~Filters.command, get_position_side)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)


set_risk_management_handler = ConversationHandler(
    entry_points=[CommandHandler('setrisk', set_risk)],
    states={
        ENTER_RISK_PERCENTAGE: [MessageHandler(Filters.text & ~Filters.command, receive_max_risk_percentage)],
        ENTER_MAX_LOSSES: [MessageHandler(Filters.text & ~Filters.command, receive_max_losses_per_day)],
        ENTER_MAX_LEVERAGE: [MessageHandler(Filters.text & ~Filters.command, receive_max_leverage)],
        ENTER_DAILY_PROFIT_TARGET: [MessageHandler(Filters.text & ~Filters.command, receive_daily_profit_target)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)


def setup_telegram_bot(telegram_token):
    # Initialize the Telegram bot
    bot = telegram.Bot(token=telegram_token)
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(conv_handler)

    dispatcher.add_handler(CommandHandler('openlong', open_long))
    dispatcher.add_handler(CommandHandler('openshort', open_short))

    order_handler = CommandHandler('open_order', start_order)    
    dispatcher.add_handler(order_handler)

    
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    check_balances_handler = CommandHandler('balances', check_balances)
    dispatcher.add_handler(check_balances_handler)

    dispatcher.add_handler(set_api_conversation_handler)
    dispatcher.add_handler(set_risk_management_handler)

    clear_risk_params_handler = CommandHandler('clearrisk', clear_risk_params)
    clear_api_credentials_handler = CommandHandler('clearapi', clear_api_credentials)

    # Add these handlers to the dispatcher
    dispatcher.add_handler(clear_risk_params_handler)
    dispatcher.add_handler(clear_api_credentials_handler)


    dispatcher.add_handler(CommandHandler('check_price', check_price))
    dispatcher.add_handler(CommandHandler('get_ohlc', get_ohlc))
    dispatcher.add_handler(CommandHandler('top_gainers', view_top_gainers))
    dispatcher.add_handler(CommandHandler('top_losers', view_top_losers))

    dispatcher.add_handler(CommandHandler('setapi', set_api))
    dispatcher.add_handler(set_commands_handler)
    dispatcher.add_handler(CommandHandler('help', help_command))



    updater.start_polling()
    updater.idle()
