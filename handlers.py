from telebot import TeleBot, types

import utils
from call_types import CallTypes


def start_command_handler(bot: TeleBot, message):
    find_tours_button = utils.make_inline_button(
        text='🏝 Найти туры',
        CallType=CallTypes.FindTours,
    )
    about_button = utils.make_inline_button(
        text='ℹ️ О нас',
        CallType=CallTypes.About,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(find_tours_button)
    keyboard.add(about_button)

    bot.send_message(
        text='<b>🛠 Меню</b>',
        chat_id=message.chat.id,
        reply_markup=keyboard,
    )


def find_tours_callback_query_handler(bot: TeleBot, call):
    