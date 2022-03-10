import telebot

import handlers
from call_types import CallTypes


TOKEN = '5242049055:AAEe6YxDOuZfqsAouBxQRTNDbh_wg1r2eSI'

bot = telebot.TeleBot(
    token=TOKEN,
    threaded=False,
    parse_mode='HTML',
)


@bot.message_handler(content_types=['text'])
def message_handler(message):
    if message.text == '/start':
        handlers.start_command_handler(bot, message)


callback_query_handlers = {
    CallTypes.FindTours: handlers.find_tours_callback_query_handler,
    CallTypes.Country: handlers.country_callback_query_handler,
    CallTypes.Region: handlers.region_callback_query_handler,
    CallTypes.DepartyCity: handlers.departy_city_callback_query_handler,
    CallTypes.Month: handlers.month_callback_query_handler,
    CallTypes.Day: handlers.day_callback_query_handler,
    CallTypes.Adult: handlers.adult_callback_query_handler,
    CallTypes.Child: handlers.child_callback_query_handler,
    CallTypes.ChildAges: handlers.child_ages_callback_query_handler,
}


@bot.callback_query_handler(func=lambda _: True)
def callback_query_handler(call):
    call_type = CallTypes.parse_data(call.data)
    for CallType, query_handler in callback_query_handlers.items():
        if call_type.__class__.__name__ == CallType.__name__:
            query_handler(bot, call)
            break


if __name__ == "__main__":
    # bot.polling()
    bot.infinity_polling()
