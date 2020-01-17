import logging

from functools import partial
from telegram.ext import Updater, CommandHandler

from lufthansa_api import LufthansaAPI
from handlers import find_flight, weekend_trip
import settings

logging.basicConfig(format = '%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

def main():

    mybot = Updater(settings.TELEGRAM_API_KEY)

    dp = mybot.dispatcher

    lh_api = LufthansaAPI(settings.LH_CLIENT_ID, settings.LH_CLIENT_SECRET)

    dp.add_handler(CommandHandler("find_flight", partial(find_flight, api=lh_api), pass_user_data=False))
    dp.add_handler(CommandHandler("weekend_trip", partial(weekend_trip, api=lh_api), pass_user_data=False))

    mybot.start_polling()
    mybot.idle()

if __name__ == "__main__":
    main()