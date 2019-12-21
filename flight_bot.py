import logging

from telegram.ext import Updater, CommandHandler

from flight_info import get_auth_token
from handlers import *
import settings

logging.basicConfig(format = '%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

def main():

    get_auth_token()

    mybot = Updater(settings.TELEGRAM_API_KEY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("find_flight", find_flight, pass_user_data=True))

    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()