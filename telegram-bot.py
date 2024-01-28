from telegram import Update
from telegram.constants import ParseMode

from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes
import logging
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import InlineQueryHandler
import binancep2p
import time
import json
import asyncio
import prettytable as pt
import configparser
import threading

config = configparser.ConfigParser()
config.read('telegrambot.config')
TOKEN = config.get('Section1', 'TOKEN')
HKDUSD_fx = config.get('Section1', 'HKDUSD')

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def update_FX():
    fx = binancep2p.request_fx()
    HKDUSD_fx = fx
    print(HKDUSD_fx)

# set_interval(update_FX,10)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


async def poll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    res = binancep2p.request_p2p()
    # print(res)
    table = pt.PrettyTable(['Price', 'Min', 'Max'])
    table.align['Price'] = 'l'
    table.align['Min'] = 'r'
    table.align['Max'] = 'r'

    for item in res:
        table.add_row([item['price'], item['min_amount'], item['max_amount']])

    message = f"<pre>{table}</pre>"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML)


contact_list = []
pause = False


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in contact_list:
        contact_list.remove(update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="user removed from push notification subscription")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="user is not in the push notification subscription")
    print(contact_list, "unsubscribed")


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # add user to notification
    if update.effective_chat.id in contact_list:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="user already added to push notification subscription")
    else:
        contact_list.append(update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text="user added to push notification subscription")

    print(contact_list, "subscribed")


async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    poll_handler = CommandHandler('poll', poll)
    subscribe_handler = CommandHandler('subscribe', subscribe)
    unsubscribe_handler = CommandHandler('unsubscribe', unsubscribe)

    application.add_handler(start_handler)
    application.add_handler(echo_handler)
    application.add_handler(poll_handler)
    application.add_handler(subscribe_handler)
    application.add_handler(unsubscribe_handler)

    # Other handlers
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    # application.run_polling() # dont want blocking

    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    counter = 0

    while ~pause:
        print('requesting')
        res = binancep2p.request_p2p()
        if counter % (6*60) == 0:
            fx = float(binancep2p.request_fx()) + 0.01
            print(fx)

        # filter bot
        if float(res[0]["price"]) > fx:
            print('more than', fx)
        else:
            print('less or equal to', fx, '... sending to subs')
            table = pt.PrettyTable(['Price', 'Min', 'Max'])
            table.align['Price'] = 'l'
            table.align['Min'] = 'r'
            table.align['Max'] = 'r'

            for item in res:
                table.add_row(
                    [item['price'], item['min_amount'], item['max_amount']])

            message = f"<pre>{table}</pre>"

            for contact in contact_list:
                await application.bot.send_message(chat_id=contact, text="Low exchange rate found")
                await application.bot.send_message(chat_id=contact, text=message, parse_mode=ParseMode.HTML)
        
        counter = counter + 1
        await asyncio.sleep(10)

    await application.updater.stop()
    await application.stop()
    await application.shutdown()

if __name__ == '__main__':
    asyncio.run(main())
