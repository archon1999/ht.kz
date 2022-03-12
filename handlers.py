import datetime
import locale
from collections import defaultdict

import ht_parser
import utils
from call_types import CallTypes

import flag
from telebot import TeleBot, types
from django.core.paginator import Paginator


search_filter_dict = defaultdict(dict)
locale.setlocale(locale.LC_ALL, 'ru_RU.utf8')


async def start_command_handler(bot: TeleBot, message):
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

    await bot.send_message(
        text='<b>🛠 Меню</b>',
        chat_id=message.chat.id,
        reply_markup=keyboard,
    )


async def find_tours_callback_query_handler(bot: TeleBot, call):
    buttons = []
    countries = ht_parser.get_countries()
    for country_id in countries:
        country = countries[country_id]
        flag_emoji = flag.flag(f':{country["code"]}:')
        text = flag_emoji + ' ' + country["name"]
        country_button = utils.make_inline_button(
            text=text,
            CallType=CallTypes.Country,
            id=country_id,
        )
        buttons.append(country_button)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    text = '<b>❓В какую страну вы бы хотели полететь?\n🖋 Выберите страну</b>'
    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


async def country_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    country_id = call_type.id
    search_filter_dict[call.message.id]['country_id'] = country_id
    countries = ht_parser.get_countries()
    country = countries[country_id]
    country_regions = country['regions']
    buttons = []
    for region_id, region in country_regions.items():
        country = countries[country_id]
        flag_emoji = flag.flag(f':{country["code"]}:')
        text = flag_emoji + ' ' + region["name"]
        country_button = utils.make_inline_button(
            text=text,
            CallType=CallTypes.Region,
            id=region_id,
        )
        buttons.append(country_button)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)    
    countries_button = utils.make_inline_button(
        text='🔙 Все страны',
        CallType=CallTypes.FindTours,
    )
    keyboard.add(countries_button)
    text = '<b>❓В какой город?\n🖋 Выберите регион</b>'
    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


async def region_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    region_id = call_type.id
    search_filter_dict[call.message.id]['region_id'] = region_id
    cities = ht_parser.get_depart_cities()
    buttons = []
    for city_id, city in cities.items():
        text = city['name']
        country_button = utils.make_inline_button(
            text=text,
            CallType=CallTypes.DepartyCity,
            id=city_id,
        )
        buttons.append(country_button)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    country_id = search_filter_dict[call.message.id]['country_id']
    countries_button = utils.make_inline_button(
        text='🔙 Все регионы',
        CallType=CallTypes.Country,
        id=country_id,
    )
    keyboard.add(countries_button)
    text = '<b>❓С какого города?\n🖋 Выберите город</b>'
    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


async def departy_city_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    city_id = call_type.id
    search_filter_dict[call.message.id]['departy_city_id'] = city_id

    buttons = []
    for month in range(1, 13):
        month_title = datetime.date(2022, month, 1).strftime('%B')
        month_button = utils.make_inline_button(
            text=month_title.title(),
            CallType=CallTypes.Month,
            number=month,
        )
        buttons.append(month_button)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    region_id = search_filter_dict[call.message.id]['region_id']
    region_button = utils.make_inline_button(
        text='🔙 С какого города?',
        CallType=CallTypes.Region,
        id=region_id,
    )
    keyboard.add(region_button)

    text = '<b>❓В какой месяц?\n🖋 Выберите месяц</b>'
    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


async def month_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    month = call_type.number
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    year = current_year + (current_month > month)
    search_filter_dict[call.message.id]['month'] = month
    search_filter_dict[call.message.id]['year'] = year

    buttons = []
    dt = datetime.datetime(year=year,
                           month=month,
                           day=1)
    while dt.month == month:
        day_button = utils.make_inline_button(
            text=str(dt.day),
            CallType=CallTypes.Day,
            number=dt.day,
        )
        buttons.append(day_button)
        dt += datetime.timedelta(days=1)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    city_id = search_filter_dict[call.message.id]['departy_city_id']
    city_button = utils.make_inline_button(
        text='🔙 Месяц',
        CallType=CallTypes.DepartyCity,
        id=city_id,
    )
    keyboard.add(city_button)

    text = '<b>❓В какой день?\n🖋 Выберите день</b>'
    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


async def day_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    day = call_type.number
    search_filter_dict[call.message.id]['day'] = day

    buttons = []
    for i in range(1, 11):
        adult_button = utils.make_inline_button(
            text=str(i),
            CallType=CallTypes.Adult,
            number=i,
        )
        buttons.append(adult_button)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    month = search_filter_dict[call.message.id]['month']
    month_button = utils.make_inline_button(
        text='🔙 День',
        CallType=CallTypes.Month,
        number=month,
    )
    keyboard.add(month_button)

    text = '<b>❓Сколько взрослых?\n🖋 Выберите</b>'
    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


async def adult_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    adult = call_type.number
    search_filter_dict[call.message.id]['adult'] = adult
    buttons = []
    for i in range(0, 11):
        child_button = utils.make_inline_button(
            text='Детей нет' if i == 0 else str(i),
            CallType=CallTypes.Child,
            number=i,
        )
        buttons.append(child_button)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    day = search_filter_dict[call.message.id]['day']
    day_button = utils.make_inline_button(
        text='🔙 Количество взрослых',
        CallType=CallTypes.Day,
        number=day,
    )
    keyboard.add(day_button)

    text = '<b>❓Сколько детей?\n🖋 Выберите</b>'
    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


async def child_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    child = call_type.number
    if child == 0:
        await send_tours(bot, call)
        return

    search_filter_dict[call.message.id]['child'] = child
    buttons = []
    for i in range(1, 13):
        child_button = utils.make_inline_button(
            text=str(i),
            CallType=CallTypes.ChildAges,
            number=i,
        )
        buttons.append(child_button)

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    adult = search_filter_dict[call.message.id]['adult']
    adult_button = utils.make_inline_button(
        text='🔙 Количество детей',
        CallType=CallTypes.Adult,
        number=adult,
    )
    keyboard.add(adult_button)

    text = '<b>❓Возраст детей?\n🖋 Выберите</b>'
    await bot.edit_message_text(
        text=text,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


async def child_ages_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    child_ages = call_type.number
    search_filter_dict[call.message.id]['child_ages'] = child_ages
    await send_tours(bot, call)


def get_search_filter_result_info(data: ht_parser.SearchFilterResult) -> str:
    return f'{"⭐️"*data.rating_star} <i>{data.rating}</i>\n<b><u>{data.title}</u></b>\n\n<i>{data.region}</i>'


def get_day_buttons(search_filter_result_index):
    buttons = []
    for number in range(3, 15):
        buttons.append(utils.make_inline_button(
            text=str(number),
            CallType=CallTypes.FindToursDay,
            day=number,
            index=search_filter_result_index,
        ))

    return buttons


async def send_tours(bot: TeleBot, call):
    global search_filter_dict
    await bot.edit_message_text(
        text='<b>🔁 Идет поиск туров</b>',
        chat_id=call.message.chat.id,
        message_id=call.message.id,
    )

    result, html = await ht_parser.parse_tours(search_filter_dict[call.message.id])
    if not result:
        text = '<b>❌ По вашему запросу ничего не найдено</b>'
        await bot.edit_message_text(
            text=text,
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
    else:
        search_filter_dict[call.message.id]['search_filter_result'] = result
        search_filter_dict[call.message.id]['html'] = html
        data = result[0]
        paginator = Paginator(result, 1)
        page = paginator.get_page(1)
        await bot.edit_message_text(
            text='<b>📶 Результаты поиска</b>',
            chat_id=call.message.chat.id,
            message_id=call.message.id,
        )
        text = utils.text_to_double_line(get_search_filter_result_info(data))
        text = '<b>🏝 Тур</b>\n' + text
        keyboard = utils.make_page_keyboard(
            page=page,
            CallType=CallTypes.SearchResult,
        )
        keyboard.add(utils.make_inline_button(
            text='Показать туры (Выберите количество дней)',
            CallType=CallTypes.Nothing,
        ))
        buttons = get_day_buttons(0)
        keyboard.add(*buttons)
        message = await bot.send_photo(
            photo=data.image_src,
            chat_id=call.message.chat.id,
            caption=text,
            reply_markup=keyboard,
        )
        search_filter_dict[message.id] = search_filter_dict[call.message.id]


async def search_result_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    page_number = call_type.page
    result = search_filter_dict[call.message.id]['search_filter_result']
    data = result[page_number-1]
    paginator = Paginator(result, 1)
    page = paginator.get_page(page_number)
    keyboard = utils.make_page_keyboard(
        page=page,
        CallType=CallTypes.SearchResult,
    )
    keyboard.add(utils.make_inline_button(
        text='Показать туры (Выберите количество дней)',
        CallType=CallTypes.Nothing,
    ))
    buttons = get_day_buttons(page_number-1)
    keyboard.add(*buttons)
    text = utils.text_to_double_line(get_search_filter_result_info(data))
    text = '<b>🏝 Тур</b>\n' + text
    await bot.edit_message_caption(
        message_id=call.message.id,
        chat_id=call.message.chat.id,
        caption=text,
        reply_markup=keyboard,
    )


async def find_tours_day_callback_query_handler(bot: TeleBot, call):
    global search_filter_dict
    call_type = CallTypes.parse_data(call.data)
    day = call_type.day
    index = call_type.index
    search_filter = search_filter_dict[call.message.id]
    tours = await ht_parser.parse_tours_day(
        search_filter=search_filter,
        index=index,
        day=day,
    )
    tours_info = str()
    for index, tour in enumerate(tours, 1):
        tour_info = '  '.join([f'<b>{tour.date}</b>', 
                               f'<i>{tour.departy_city}</i>',
                               f'<code>{tour.days}</code>',
                               f'<b>{tour.food}</b>',
                               f'<i>{tour.people}</i>',
                               f'<b>{tour.price}</b>'])
        tours_info += tour_info + '\n'

    text = '<b>🏝 Туры</b>' + utils.text_to_double_line(tours_info)
    await bot.send_message(call.message.chat.id, text)
