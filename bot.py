import telebot

import handlers
from call_types import CallTypes


TOKEN = '5242049055:AAEe6YxDOuZfqsAouBxQRTNDbh_wg1r2eSI'

bot = telebot.TeleBot(
    token=TOKEN,
    num_threads=3,
    parse_mode='HTML',
)


@bot.message_handler(content_types=['text'])
def message_handler(message):
    if message.text == '/start':
        handlers.start_command_handler(bot, message)


callback_query_handlers = {
}


@bot.callback_query_handler(func=lambda _: True)
def callback_query_handler(call):
    call_type = CallTypes.parse_data(call.data)
    for CallType, query_handler in handlers.items():
        if call_type.__class__.__name__ == CallType.__name__:
            query_handler(bot, call)
            break


if __name__ == "__main__":
    # bot.polling()
    bot.infinity_polling()
