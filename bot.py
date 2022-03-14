import asyncio
from collections import defaultdict

from telebot import async_telebot, TeleBot

import handlers
from call_types import CallTypes

FEEDBACK_CHAT_ID = '5055897016'
TOKEN = '5242049055:AAEe6YxDOuZfqsAouBxQRTNDbh_wg1r2eSI'

bot = async_telebot.AsyncTeleBot(
    token=TOKEN,
    parse_mode='HTML',
)

state_dict = defaultdict(int)


@bot.message_handler(content_types=['text'])
async def message_handler(message):
    global state_dict
    if state_dict[message.chat.id]:
        await handlers.feedback_message_handler(bot, message)
        state_dict[message.chat.id] = 0

    if message.text == '/start':
        await handlers.start_command_handler(bot, message)


async def feedback_callback_query_handler(bot: TeleBot, call):
    global state_dict
    state_dict[call.message.chat.id] = 1
    text = '<b>🖋 Напишите текст</b>'
    await bot.send_message(call.message.chat.id, text)


async def feedback_message_handler(bot: TeleBot, message):
    await bot.send_message(
        chat_id=FEEDBACK_CHAT_ID,
        text=message.text,
    )
    await bot.send_message(
        chat_id=message.chat.id,
        text='<b>✔️ Отправлено</b>'
    )


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
    CallTypes.SearchResult: handlers.search_result_callback_query_handler,
    CallTypes.FindToursDay: handlers.find_tours_day_callback_query_handler,
    CallTypes.Feedback: feedback_callback_query_handler,
    CallTypes.About: handlers.about_callback_query_handler,
}


@bot.callback_query_handler(func=lambda _: True)
async def callback_query_handler(call):
    call_type = CallTypes.parse_data(call.data)
    for CallType, query_handler in callback_query_handlers.items():
        if call_type.__class__.__name__ == CallType.__name__:
            await query_handler(bot, call)
            break


if __name__ == "__main__":
    asyncio.run(bot.polling())
    # asyncio.run(bot.infinity_polling())
