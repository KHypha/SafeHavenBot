import telegram
import sqlite3
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from binance_api.binance_client import BinanceFuturesAPI
from telegram import Update, InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from watchdog.observers import Observer  # Add this import
from watchdog.events import FileSystemEventHandler  # Add this import
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
# Define conversation states
SELECT_ORDER_TYPE, ENTER_SYMBOL, ENTER_SIDE, ENTER_POSITION_SIDE, ENTER_QUANTITY, ENTER_PRICE, ENTER_STOP_PRICE, ENTER_LIMIT_PRICE = range(8)


# Initialize the Telegram bot
def start(update, context):
    update.message.reply_text("Welcome to the Binance Futures bot! You can use the following commands:\n"
                              "/setapi - Set up your Binance API credentials\n"
                              "/balances - Check your account balances\n"
                              "/open_order - Open a new order\n"
                              "/cancel - Cancel the current operation")
    return ConversationHandler.END  # End the conversation

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

def receive_api_key(update, context):
    api_key = update.message.text.strip()
    context.user_data['api_key'] = api_key
    update.message.reply_text("API Key saved. Now, please enter your API secret:")
    return ENTER_API_SECRET

def receive_api_secret(update, context):
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

def check_balances(update, context):
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)

    if api_key and api_secret:
        binance_api = BinanceFuturesAPI(api_key, api_secret)
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
    else:
        update.message.reply_text("API credentials not found. Please set up your credentials using /start.")

def open_long(update, context):
    chat_id = update.message.chat_id
    
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)

    if api_key and api_secret:
        binance_api = BinanceFuturesAPI(api_key, api_secret)


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

    else:
        update.message.reply_text("API credentials not found. Please set up your credentials using /start.")

def display_orders(update, context):
    chat_id = update.message.chat_id
    
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)

    if api_key and api_secret:
        binance_api = BinanceFuturesAPI(api_key, api_secret)
    
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
    
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)

    if api_key and api_secret:
        binance_api = BinanceFuturesAPI(api_key, api_secret)
    
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
    
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)

    if api_key and api_secret:
        binance_api = BinanceFuturesAPI(api_key, api_secret)


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
    
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)

    if api_key and api_secret:
        binance_api = BinanceFuturesAPI(api_key, api_secret)

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
    update.message.reply_text("Let's start opening an order. Please choose the order type:",
                              reply_markup=ReplyKeyboardMarkup([['Limit Order', 'Market Order', 'Stop-Limit Order', 'Take-Profit Order', 'Stop-Loss Order']],
                                                               one_time_keyboard=True))
    return SELECT_ORDER_TYPE

def select_order_type(update, context):
    user_input = update.message.text
    context.user_data['order_type'] = user_input
    if user_input == 'market_long':
        context.user_data['side'] = 'BUY'
        update.message.reply_text("Please enter the symbol for the order:")
        return ENTER_SYMBOL   

    elif user_input == 'market_short':
        context.user_data['side'] = 'SELL'
        update.message.reply_text("Please enter the symbol for the order:")
        return ENTER_SYMBOL
    else:
        update.message.reply_text("Please enter the side for the order:")
        return ENTER_SIDE

def receive_side(update, context):
    side = update.message.text
    context.user_data['side'] = side
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)
    
    binance_api = BinanceFuturesAPI(api_key, api_secret, context)
    hedge_mode = binance_api.check_hedge_mode()
    order_type = context.user_data.get('order_type')
    if hedge_mode :
        if order_type == 'take_profit':
            context.user_data['position_side'] = 'LONG' if side =='BUY' else 'SHORT'
        elif order_type == 'stop_loss':
            context.user_data['position_side'] = 'LONG' if side =='SELL' else 'SHORT'
        else:
            update.message.reply_text("Please enter the Position Side (LONG or SHORT):")
            return ENTER_POSITION_SIDE
    
    update.message.reply_text("Please enter the symbol for the order:")
    return ENTER_SYMBOL 
    
  
def receive_position_side(update, context):
    position_side = update.message.text.upper()
    if position_side in ['LONG', 'SHORT']:
        context.user_data['position_side'] = position_side
        update.message.reply_text("Please enter the symbol for the order:")
        return ENTER_SYMBOL
    else:
        update.message.reply_text("Invalid position side. Please enter 'LONG' or 'SHORT':")
        return ENTER_POSITION_SIDE
    
def receive_symbol(update, context):
    symbol = update.message.text
    context.user_data['symbol'] = symbol

    # Determine the order type based on the context
    order_type = context.user_data.get('order_type')

    if order_type in ['market_long', 'market_short', 'limit', 'stop_limit']:
        update.message.reply_text("Please enter the quantity for the order:")
        return ENTER_QUANTITY  # Proceed to quantity
    elif order_type in ['stop_loss', 'take_profit']:
        update.message.reply_text("Please enter the price for the order:")
        return ENTER_STOP_PRICE  # Proceed to price
    else:
        update.message.reply_text("Invalid order type. Please enter the order type again")
        return SELECT_ORDER_TYPE
    
def receive_quantity(update, context):
    quantity = update.message.text
    context.user_data['quantity'] = quantity

    # Determine the order type based on the context
    order_type = context.user_data.get('order_type')

    if order_type == 'market_long' or order_type == 'market_short':
        # For market_long, place a market order with buy side (LONG)
        place_order(update, context)

    elif order_type == 'limit' or  order_type == 'stop_limit':
        # For limit order, proceed to collecting price
        # proceed to collecting stop and limit prices
        update.message.reply_text("Please enter the limit price:")
        return ENTER_LIMIT_PRICE

    return ConversationHandler.END

def receive_limit_price(update, context):
    limit_price = update.message.text
    context.user_data['limit_price'] = limit_price
    # Determine the order type and additional parameters based on the context
    order_type = context.user_data.get('order_type')

    # For stop_limit order, place the order\
    if order_type == 'limit':
        place_order(update, context)
    elif order_type == 'stop_limit':
        update.message.reply_text("Please enter the stop price:")
        return ENTER_STOP_PRICE

    return ConversationHandler.END

   
def receive_stop_price(update, context):
    stop_price = update.message.text
    context.user_data['stop_price'] = stop_price
    order_type = context.user_data.get('order_type')
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)
    
    binance_api = BinanceFuturesAPI(api_key, api_secret, context)
    if order_type in ['stop_loss', 'take_profit']:
        #get and assign qty
        quantity = binance_api.get_position_quantity
        context.user_data['quantity'] = quantity

    place_order(update, context)


def place_order(update, context):
    # Additional code for getting API credentials, similar to what you've done before
    user_id = update.message.from_user.id
    api_key, api_secret = get_credentials(user_id)
    
    binance_api = BinanceFuturesAPI(api_key, api_secret, context)
    order_type = context.user_data.get('order_type')
    
    if order_type == 'market_long':
        order = binance_api.place_market_order()
    elif order_type == 'market_short':
        order = binance_api.place_market_order()
    elif order_type == 'limit':
        order = binance_api.place_limit_order()
    elif order_type == 'stop_limit':
        order = binance_api.place_stop_limit_order()
    elif order_type == 'stop_loss':
        order = binance_api.place_stop_loss_order()

    elif order_type == 'take_profit':
        order = binance_api.place_take_profit_order()

    context.user_data.clear()  # Clear user data

    update.message.reply_text(f"Order placed:\n{order}")
    return ConversationHandler.END

def cancel(update, context):
    update.message.reply_text("Order placement canceled.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

# Handler to cancel the API setting conversation
def cancel_set_api(update, context):
    update.message.reply_text("API setting canceled.")
    return ConversationHandler.END  # End the conversation

# Create the ConversationHandler for setting API credentials
set_api_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('setapi', set_api)],
    states={
        ENTER_API_KEY: [MessageHandler(Filters.text & ~Filters.command, receive_api_key)],
        ENTER_API_SECRET: [MessageHandler(Filters.text & ~Filters.command, receive_api_secret)],
    },
    fallbacks=[CommandHandler('cancel', cancel_set_api)]
)
# Create a conversation handler for the order placement process
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('order', start_order)],
    states={
        SELECT_ORDER_TYPE: [MessageHandler(Filters.text & ~Filters.command, select_order_type)],
        ENTER_SYMBOL: [MessageHandler(Filters.text & ~Filters.command, receive_symbol)],
        ENTER_QUANTITY: [MessageHandler(Filters.text & ~Filters.command, receive_quantity)],
        ENTER_SIDE: [MessageHandler(Filters.text & ~Filters.command, receive_side)],
        ENTER_STOP_PRICE: [MessageHandler(Filters.text & ~Filters.command, receive_stop_price)],
        ENTER_LIMIT_PRICE: [MessageHandler(Filters.text & ~Filters.command, receive_limit_price)],
        ENTER_POSITION_SIDE: [MessageHandler(Filters.text & ~Filters.command, receive_position_side)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
    allow_reentry=True
)


def open_long(update, context):
    context.user_data['order_type'] = 'open_long'  # Indicate the order type
    return start_order(update, context)

def open_short(update, context):
    context.user_data['order_type'] = 'open_short'  # Indicate the order type
    return start_order(update, context)

def take_profit(update, context):
    context.user_data['order_type'] = 'take_profit'  # Indicate the order type
    return start_order(update, context)

def stop_loss(update, context):
    context.user_data['order_type'] = 'stop_loss'  # Indicate the order type
    return start_order(update, context)

def setup_telegram_bot(telegram_token):
    # Initialize the Telegram bot
    bot = telegram.Bot(token=telegram_token)
    updater = Updater(token=telegram_token, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(conv_handler)

    dispatcher.add_handler(CommandHandler('openlong', open_long))
    dispatcher.add_handler(CommandHandler('openshort', open_short))
    dispatcher.add_handler(CommandHandler('takeprofit', take_profit))
    dispatcher.add_handler(CommandHandler('stoploss', stop_loss))
    
    order_handler = CommandHandler('open_order', start_order)    
    dispatcher.add_handler(order_handler)

    
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    check_balances_handler = CommandHandler('balances', check_balances)
    dispatcher.add_handler(check_balances_handler)

    dispatcher.add_handler(set_api_conversation_handler)

    updater.start_polling()
    updater.idle()
