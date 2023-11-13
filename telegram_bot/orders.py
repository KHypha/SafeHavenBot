SELECT_ORDER_TYPE, ENTER_SYMBOL, ENTER_SIDE, ENTER_POSITION_SIDE, ENTER_QUANTITY, ENTER_PRICE, ENTER_STOP_PRICE, ENTER_LIMIT_PRICE = range(8)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
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

from telegram_bot import bot
# Define conversation states

def start_order(update, context):
    context.user_data.clear()  # Clear any previous user data
    update.message.reply_text("Let's start opening an order. Please choose the order type:",
                              reply_markup=ReplyKeyboardMarkup([['Limit Order', 'Market Order', 'Stop-Limit Order', 'Take-Profit Order', 'Stop-Loss Order']],
                                                               one_time_keyboard=True))
    return SELECT_ORDER_TYPE

def select_order_type(update, context):
    user_input = update.message.text
    context.user_data['order_type'] = user_input
    update.message.reply_text("Please enter the symbol for the order:")
    return ENTER_SYMBOL
    

def receive_symbol(update, context):
    symbol = update.message.text
    context.user_data['symbol'] = symbol

    # Determine the order type based on the context
    order_type = context.user_data.get('order_type')

    if order_type == 'market_long' or order_type == 'market_short':
        return receive_quantity(update, context)  # Proceed to quantity
    elif order_type == 'limit':
        return receive_quantity(update, context)  # Proceed to quantity
    elif order_type == 'stop_limit':
        return receive_quantity(update, context)  # Proceed to quantity
    elif order_type == 'stop_loss' or order_type == 'take_profit':
        return receive_price(update, context)  # Proceed to price
      
def receive_quantity(update, context):
    quantity = update.message.text
    context.user_data['quantity'] = quantity

    user_id = update.message.from_user.id
    api_key, api_secret = bot.get_credentials(user_id)

    if 'symbol' in context.user_data and 'quantity' in context.user_data:
        binance_api = BinanceFuturesAPI(api_key, api_secret)

        symbol = context.user_data['symbol']
        quantity = context.user_data['quantity']

        # Determine the order type based on the context
        order_type = context.user_data.get('order_type')

        if order_type == 'market_long':
            # For market_long, place a market order with buy side (LONG)
            order = binance_api.place_market_order(symbol, 'BUY', quantity, position_side='LONG')
        elif order_type == 'market_short':
            # For market_short, place a market order with sell side (SHORT)
            order = binance_api.place_market_order(symbol, 'SELL', quantity, position_side='SHORT')
        elif order_type == 'limit':
            # For limit order, proceed to collecting price
            update.message.reply_text("Please enter the side:")
            return ENTER_SIDE
        elif order_type == 'stop_limit':
            # For stop_limit order, proceed to collecting stop and limit prices
            update.message.reply_text("Please enter the stop price:")
            return ENTER_STOP_PRICE
        elif order_type == 'stop_loss' or order_type == 'take_profit':
            # For stop_loss and take_profit orders, proceed to collecting side
            update.message.reply_text("Please enter the side (BUY or SELL):")
            return ENTER_SIDE
    else:
        update.message.reply_text("Not all required order parameters were provided. The order was not placed.")

    # End the conversation
    context.user_data.clear()
    return ConversationHandler.END

def receive_side(update, context):
    side = update.message.text
    context.user_data['side'] = side

    user_id = update.message.from_user.id
    api_key, api_secret = bot.get_credentials(user_id)

    if 'symbol' in context.user_data and 'quantity' in context.user_data and 'side' in context.user_data:
        binance_api = BinanceFuturesAPI(api_key, api_secret)

        symbol = context.user_data['symbol']
        quantity = context.user_data['quantity']
        side = context.user_data['side']

        # Determine the order type based on the context
        order_type = context.user_data.get('order_type')

        if order_type == 'limit':
            # For limit order, proceed to collecting price
            update.message.reply_text("Please enter the price:")
            return ENTER_LIMIT_PRICE
        elif order_type == 'stop_limit':
            # For stop_limit order, proceed to collecting stop and limit prices
            update.message.reply_text("Please enter the stop price:")
            return ENTER_LIMIT_PRICE
        elif order_type == 'stop_loss':
            # For stop_loss order, place the stop_loss order
            order = binance_api.place_stop_loss_order(symbol, context.user_data['price'], side, position_side='LONG' if side == 'BUY' else 'SHORT')
        elif order_type == 'take_profit':
            # For take_profit order, place the take_profit order
            order = binance_api.place_take_profit_order(symbol, context.user_data['price'], side, position_side='LONG' if side == 'BUY' else 'SHORT')

        # Additional code for handling specific orders, if needed

    else:
        update.message.reply_text("Not all required order parameters were provided. The order was not placed.")
        context.user_data.clear()
        return ConversationHandler.END
  
def receive_price(update, context):
    price = update.message.text
    context.user_data['price'] = price

    # Determine the order type and additional parameters based on the context
    order_type = context.user_data.get('order_type')
    hedge_mode = context.user_data.get('hedge_mode')

    user_id = update.message.from_user.id
    api_key, api_secret = bot.get_credentials(user_id)

    if 'symbol' in context.user_data and 'quantity' in context.user_data and 'price' in context.user_data:
        binance_api = BinanceFuturesAPI(api_key, api_secret)

        symbol = context.user_data['symbol']
        quantity = context.user_data['quantity']
        price = context.user_data['price']

        if hedge_mode and 'position_side' not in context.user_data:
            # If hedge mode is enabled but position side is not set, ask the user to specify it
            update.message.reply_text("Please enter the position side (LONG or SHORT):")
            return ENTER_POSITION_SIDE

        if order_type == 'market_long':
            # For market_long, place a market order with buy side (LONG)
            order = binance_api.place_market_order(symbol, 'BUY', quantity, position_side=context.user_data.get('position_side', 'LONG'))
        elif order_type == 'market_short':
            # For market_short, place a market order with sell side (SHORT)
            order = binance_api.place_market_order(symbol, 'SELL', quantity, position_side=context.user_data.get('position_side', 'SHORT'))
        elif order_type == 'limit':
            # For limit order, proceed to collecting side
            update.message.reply_text("Please enter the side (BUY or SELL):")
            return ENTER_SIDE
        elif order_type == 'stop_limit':
            # For stop_limit order, proceed to collecting stop and limit prices
            update.message.reply_text("Please enter the stop price:")
            return ENTER_STOP_PRICE
        elif order_type == 'stop_loss' or order_type == 'take_profit':
            # For stop_loss and take_profit orders, determine the side based on hedge mode
            if hedge_mode:
                side = 'BUY' if context.user_data.get('position_side', 'LONG') == 'LONG' else 'SELL'
            else:
                # If not in hedge mode, use the side collected earlier
                side = context.user_data.get('side')

            if order_type == 'stop_loss':
                # Place the stop loss order
                order = binance_api.place_stop_loss_order(symbol, price, side)
            else:
                # Place the take profit order
                order = binance_api.place_take_profit_order(symbol, price, side)

            # Additional code for handling specific orders, if needed

        # End the conversation
        context.user_data.clear()
        update.message.reply_text(f"Order placed:\n{order}")
        return ConversationHandler.END
    else:
        update.message.reply_text("Not all required order parameters were provided. The order was not placed.")
        context.user_data.clear()
        return ConversationHandler.END
  
def receive_stop_price(update, context):
    stop_price = update.message.text
    context.user_data['stop_price'] = stop_price
    update.message.reply_text("Please enter the limit price:")
    return ENTER_LIMIT_PRICE

def receive_limit_price(update, context):
    limit_price = update.message.text
    context.user_data['limit_price'] = limit_price
    # Determine the order type and additional parameters based on the context
    order_type = context.user_data.get('order_type')
    hedge_mode = context.user_data.get('hedge_mode')
    # if hedge_mode and 'position_side' not in context.user_data:
    #     # If hedge mode is enabled but position side is not set, ask the user to specify it
    #     update.message.reply_text("Please enter the position side (LONG or SHORT):")
    #     return POSITION_SIDE

    user_id = update.message.from_user.id
    api_key, api_secret = bot.get_credentials(user_id)

    if 'symbol' in context.user_data and 'quantity' in context.user_data and 'side' in context.user_data and 'stop_price' in context.user_data and 'limit_price' in context.user_data:
        binance_api = BinanceFuturesAPI(api_key, api_secret)

        symbol = context.user_data['symbol']
        quantity = context.user_data['quantity']
        side = context.user_data['side']
        stop_price = context.user_data['stop_price']
        limit_price = context.user_data['limit_price']

        # For stop_limit order, place the order\
        if order_type == 'stop_limit':
            order = binance_api.place_stop_limit_order(symbol, quantity, stop_price, limit_price, side, position_side='LONG' if side == 'BUY' else 'SHORT')
        elif order_type == 'limit':
            order = binance_api.place_limit_order(symbol, side, quantity, limit_price, position_side='LONG' if side == 'BUY' else 'SHORT')

           # place_limit_order(update, binance_api, symbol, side, quantity, limit_price, hedge_mode)

        # Additional code for handling specific orders, if needed

    else:
        update.message.reply_text("Not all required order parameters were provided. The order was not placed.")
        context.user_data.clear()

    return ConversationHandler.END
