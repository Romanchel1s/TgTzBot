from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from config import bot_token, weather_token, news_token
import requests
import datetime
import random

TOKEN = bot_token


# получаем экземпляр `Updater`
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher


def send_keyboard(update, context):
    # Создаем кнопки
    button1 = InlineKeyboardButton("Help me", callback_data="help")
    button2 = InlineKeyboardButton("Echo!", callback_data="echo")
    button3 = InlineKeyboardButton("Weather", callback_data="weather")
    button4 = InlineKeyboardButton("News", callback_data="news")
    button5 = InlineKeyboardButton("Joke", callback_data="joke")
    button6 = InlineKeyboardButton("Random", callback_data="random")

    # Создаем клавиатуру и добавляем кнопки
    keyboard = [[button1, button2, button3, button4, button5, button6]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправляем сообщение с клавиатурой
    update.message.reply_text("Привет, я телеграм бот Ивасик, можешь потыкать кнопки ниже:", reply_markup=reply_markup)


def button_callback(update, context):
    query = update.callback_query
    if query.data == "help":
        # Если нажата кнопка "Help me", отправляем команду /help в чат
        context.bot.send_message(chat_id=query.message.chat_id, text="/help")
        help_command(update, context)
    elif query.data == "echo":
        # Если нажата кнопка "Echo!", отправляем сообщение text в чат
        context.bot.send_message(chat_id=query.message.chat_id, text="Напишите /echo <ваш текст>")
    elif query.data == "weather":
        # Если нажата кнопка "Weather", отправляем сообщение text в чат
        context.bot.send_message(chat_id=query.message.chat_id, text="Напишите /weather <город>")
    elif query.data == "random":
        # Если нажата кнопка "random", отправляем сообщение text в чат
        context.bot.send_message(chat_id=query.message.chat_id, text="Напишите /random <минимум> <максимум>")
    elif query.data == "news":
        # Если нажата кнопка "News", отправляем сообщение text в чат
        context.bot.send_message(chat_id=query.message.chat_id, text="Напишите /news <тема новости>")
    elif query.data == "joke":
        # Если нажата кнопка "Joke", отправляем команду /joke в чат
        context.bot.send_message(chat_id=query.message.chat_id, text="/joke")
        joke(update, context)


def echo(update, context):
    # Отвечает на сообщение, повторяя его
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text.replace('/echo',''))


def help_command(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Доступные команды:\n'
    '/start - приветствие пользователя и вывод меню\n'
    '/help - помощь, краткое описание команд\n'
    '/weather <город>  - актуальный прогноз погоды\n'
    '/echo <ваш текст> - эхо-ответ с переданным текстом\n'
    '/news <тема новости> - вывод последних новостей по заданной теме\n'
    '/joke - вывод случайной шутки\n'
    '/stop - прощание с пользователем и остановка работы бота\n'
    '/random - рандомное число из заданного диапазона')


def weather(update, context):
    #Прогноз погоды в city
    city = update.message.text.replace('/weather ','')
    try:
        r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_token}&units=metric")
        data = r.json()
        out_city = data['name']
        cur_weather = data['main']['temp']
        humidity = data['main']['humidity']
        pressure = data['main']['pressure']
        speedofwind = data['wind']['speed']
        sunrise_time = datetime.datetime.fromtimestamp(data['sys']['sunrise'])
        sunset_time = datetime.datetime.fromtimestamp(data['sys']['sunset'])
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Погода в городе {out_city}\n'
        f'Температура воздуха: {cur_weather}С\n'
        f'Влажность: {humidity}%\n'
        f'Давление: {pressure}\n'
        f'Скорость ветра: {speedofwind} м/с\n'
        f'Время восхода: {sunrise_time}\n'
        f'Время заката: {sunset_time}')
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Ошибка, попробуйте ещё раз')


def random_number(update, context):
    if len(context.args) < 2:
        update.message.reply_text('Используйте команду /random <минимум> <максимум>')
        return

    try:
        min_value = int(context.args[0])
        max_value = int(context.args[1])

        if min_value >= max_value:
            update.message.reply_text('Минимальное значение должно быть меньше максимального')
            return

        random_num = random.randint(min_value, max_value)
        update.message.reply_text(f'Случайное число: {random_num}')

    except ValueError:
        update.message.reply_text('Некорректные аргументы. Введите целочисленные значения для минимума и максимума.')

random_number_handler = CommandHandler('random', random_number)
dispatcher.add_handler(random_number_handler)


def news(update, context):
    try:
        news_query = update.message.text.replace('/news ','')
        r = requests.get(f"https://newsapi.org/v2/everything?q={news_query}&apiKey={news_token}")
        data = r.json()
        source_name = data['articles'][0]['source']['name']
        title = data['articles'][0]['title']
        description = data['articles'][0]['description']
        url = data['articles'][0]['url']
        context.bot.send_message(chat_id=update.effective_chat.id, text=f'Новостной ресурс: {source_name}\n'
        f'Заголовок новости: {title}\n'
        f'Описание: {description}\n'
        f'Читать дальше: {url}')
    except:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Ошибка, попробуйте ещё раз')


def joke(update, context):
    r = requests.get(f"https://official-joke-api.appspot.com/random_joke")
    data = r.json()
    setup = data['setup']
    punchline = data['punchline']
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{setup}\n'
    f'\n'
    f'{punchline}')


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Извините, я не понимаю такую команду, перейдите в /help")


def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="До скорой встречи!")
    updater.stop()

# Добавляем команды

dispatcher.add_handler(CommandHandler('random', random_number))
dispatcher.add_handler(CommandHandler("start", send_keyboard))
dispatcher.add_handler(CommandHandler("help", help_command))
dispatcher.add_handler(CommandHandler("echo", echo))
dispatcher.add_handler(CommandHandler("weather", weather))
dispatcher.add_handler(CommandHandler("news", news))
dispatcher.add_handler(CommandHandler("joke", joke))
dispatcher.add_handler(CommandHandler("stop", stop))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))
dispatcher.add_handler(CallbackQueryHandler(button_callback))

# запуск прослушивания сообщений
updater.start_polling()
