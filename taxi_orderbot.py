from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, CallbackContext, ConversationHandler
from telegram.ext.filters import Filters
from constant import TOKEN, CHAT_ID
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

ADDRESS_FROM, ADDRESS_TO, CONTACT_PHONE, PASSENGER_NAME, TIME = range(5)

def start(update, context):
    keyboard = [['/order']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    update.message.reply_text("Welcome!\n Press 'Order' to start placing your taxi order.", reply_markup=reply_markup)
    

def order(update, context):
    update.message.reply_text("Let's start with the pickup address.\nPlrase provide it in the format 'Street name 123'.")
    return ADDRESS_FROM

def address_from(update, context):
    context.user_data['address_from'] = update.message.text
    update.message.reply_text("Great!\nNow, please provide the destination address.")
    return ADDRESS_TO

def address_to(update, context):
    context.user_data['address_to'] = update.message.text
    update.message.reply_text("Perfect!\nNow, share the contact phone number in the format +8(123)55555.")
    return CONTACT_PHONE

def contact_phone(update, context):
    context.user_data['contact_phone'] = update.message.text
    update.message.reply_text("Got it!\nIf you want to provide your name , feel free to do so.\n Otherwise, just type 'skip'.")
    return PASSENGER_NAME

def passenger_name(update, context):
    user_name = update.message.text
    if user_name.lower() == 'skip':
        user_name = 'Not provided'
    context.user_data['passenger_name'] = user_name
    update.message.reply_text("Lastly,\nSpecify the time you would like the taxi to arrive.")
    return TIME

def time(update, context):
    context.user_data['time'] = update.message.text
    if all(key in context.user_data for key in ['address_from', 'address_to', 'contact_phone', 'time']):
        order_details = f"Taxi Order Details:\nFrom:{context.user_data['address_from']}\nTo: {context.user_data['address_to']}\nContact Phone: {context.user_data['contact_phone']}\nPassenger Name: {context.user_data['passenger_name']}\nTime: {context.user_data['time']}"
        context.bot.send_message(chat_id=CHAT_ID, text=order_details)
        update.message.reply_text("Taxi order placed successfully!", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        update.message.reply_text("Not enoughh information to place the order.\nPlease provide all required details.")
        return ConversationHandler.END
    
def cancel(update, context):
    update.message.reply_text("Order Canceled.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main():
    updater = Updater(TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler('start', start)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('order', order)],
        states={
            ADDRESS_FROM: [MessageHandler(Filters.text & ~Filters.command, address_from)],
            ADDRESS_TO: [MessageHandler(Filters.text & ~Filters.command, address_to)],
            CONTACT_PHONE: [MessageHandler(Filters.text & ~Filters.command, contact_phone)],
            PASSENGER_NAME: [MessageHandler(Filters.text & ~Filters.command, passenger_name)],
            TIME: [MessageHandler(Filters.text & ~Filters.command, time)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

