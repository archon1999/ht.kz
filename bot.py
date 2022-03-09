import telebot

from call_types import CallTypes
# from states import States


TOKEN = ''

bot = telebot.TeleBot(
    token=TOKEN,
    num_threads=3,
    parse_mode='HTML',
)


@bot.message_handler(content_types=['text'])
def message_handler(message):
    chat_id = message.chat.id


callback_query_handlers = {
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
