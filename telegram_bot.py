import profile
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import alpaca_trade_api as tradeapi


def start(update: Update, context: CallbackContext):
    update.message.reply_text("Hi! I'm V.I.R.O!")
    update.message.reply_text("Very Intelligent Robot Object!")
    update.message.reply_text("Chat ID is " + str(update.message.chat_id))

def list_commands(update: Update, context: CallbackContext):
    if str(update.message.chat_id) == profile.TELEGRAM_CHAT_ID:
        user = update.effective_user
        update.message.reply_text("/status for an overview and P/L of the account")
        update.message.reply_text("/positions for current status of all open positions")
        update.message.reply_text("/close to close all open positions")

def send_message(text):
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&parse_mode=Markdown&text={}".format(profile.TELEGRAM_API_KEY, profile.TELEGRAM_CHAT_ID, text)
    response = requests.get(url)
    #print(response.json())

def status(update: Update, context: CallbackContext):
    if str(update.message.chat_id) == profile.TELEGRAM_CHAT_ID:
        user = update.effective_user
        api = tradeapi.REST(
            profile.APCA_API_KEY_ID,
            profile.APCA_API_SECRET_KEY,
            profile.APCA_API_BASE_URL
        )
        account = api.get_account()

        update.message.reply_text("Equity: ${:,}".format(round(float(account.equity),2)))
        today_pl = float(account.equity) - float(account.last_equity)
        today_pl_pct = round((today_pl / float(account.last_equity)) * 100, 2)
        update.message.reply_text("Today's P/L: ${:,}   {}%".format(round(today_pl, 2), round(today_pl_pct, 2)))
        update.message.reply_text("Cash: ${:,}".format(round(float(account.cash), 2)))
        update.message.reply_text("Buying Power: ${:,}".format(round(float(account.buying_power), 2)))

        total_pl = float(account.equity) - float(30000)
        total_pl_pct = round((total_pl / float(30000)) * 100, 2)
        update.message.reply_text("Total's P/L: ${:,}   {}%".format(round(total_pl, 2), round(total_pl_pct, 2)))

def positions(update: Update, context: CallbackContext):
    if str(update.message.chat_id) == profile.TELEGRAM_CHAT_ID:
        user = update.effective_user
        update.message.reply_text("I'm checking with your broker!")

        api = tradeapi.REST(
            profile.APCA_API_KEY_ID,
            profile.APCA_API_SECRET_KEY,
            profile.APCA_API_BASE_URL
        )
        account = api.get_account()

        positions = api.list_positions()
        if positions is not None:
            for position in positions:
                update.message.reply_text("{} P/L: ${:,}   {}% Current Price: {} Entry Price: {}".format(position.symbol, round(float(position.unrealized_pl), 2), round(float(position.unrealized_plpc) * 100, 2), position.current_price, round(float(position.avg_entry_price), 2)))
        else:
            update.message.reply_text("No Positions!")

        update.message.reply_text("Equity: ${:,}".format(round(float(account.equity),2)))
        pl = float(account.equity) - float(account.last_equity)
        pl_pct = round((pl / float(account.last_equity)) * 100, 2)
        update.message.reply_text("Today's P/L: ${:,}   {}%".format(round(pl, 2), round(pl_pct, 2)))
        update.message.reply_text("Cash: ${:,}".format(round(float(account.cash), 2)))
        update.message.reply_text("Buying Power: ${:,}".format(round(float(account.buying_power), 2)))

def close(update: Update, context: CallbackContext):
    if str(update.message.chat_id) == profile.TELEGRAM_CHAT_ID:
        update.message.reply_text("Closing all positions")
        api = tradeapi.REST(
            profile.APCA_API_KEY_ID,
            profile.APCA_API_SECRET_KEY,
            profile.APCA_API_BASE_URL
        )

        positions = api.close_all_positions()
        for position in positions:    
            if position.status == 200:
                update.message.reply_text("All positions closed!")
            else:
                update.message.reply_text("Something went wrong!")

def main():
    updater = Updater(profile.TELEGRAM_API_KEY)

    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", list_commands))
    dispatcher.add_handler(CommandHandler("status", status))
    dispatcher.add_handler(CommandHandler("positions", positions))
    dispatcher.add_handler(CommandHandler("close", close))

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    print("Telegram Bot started!")
    main()