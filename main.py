import telebot
import os
from dotenv import load_dotenv
from telebot import types
from datetime import datetime
import classes

import sql_connection

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

@bot.message_handler(content_types=['text'])
# Обработка сообщений от пользователя
def start(message):
    # Создаем юзера, в котором хранится информация о поиске
    user = classes.Person()
    # Сохраняем время запроса
    user.time = datetime.now().strftime('%H:%M, %d.%m.%Y')

    # Сохраняем id чата
    user.id_chat = message.chat.id
    # Реализация функций поиска отелей
    if message.text.lower() in ('/lowprice', '/highprice', '/bestdeal'):
        # Сохраняем выбор
        user.choice = message.text.lower()
        # Функция /bestdeal
        # Для получения данных для поиска отправляем сначала в get_min_price за минимальной ценой
        if message.text.lower() == '/bestdeal':
            bot.send_message(message.from_user.id, "Напишите минимальную стоимость (USD)")
            bot.register_next_step_handler(message, get_min_price, user)
        # Функции lowprice и highprice
        # Для получения данных для поиска отправляем сразу в get_city за получением города
        else:
            bot.send_message(message.from_user.id, "Напишите название города")
            bot.register_next_step_handler(message, check, user)

    # Вывод сообщения - подсказки со всеми функциями
    # Отправляем пользователя в начало
    elif message.text.lower() == '/start' or message.text.lower() == '/help':
        bot.send_message(message.from_user.id, "/lowprice - Поиск отелей с минимальной стоимостью\n"
                                               "/highprice - Поиск отелей с максимальной стоимостью\n"
                                               "/bestdeal - Поиск отелей в заданном ценовом диапазоне и радиусе\n"
                                               "/history - История поиска")
        bot.register_next_step_handler(message, start)
    # Реализация вывода истории
    elif message.text.lower() == '/history':
        text = str(sql_connection.get_history(message.chat.id))
        if len(text) == 0:
            text = "История поиска пустая"
        bot.send_message(message.from_user.id, text)


    # Обработка остальных сообщений пользователя
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start или /help")


# Получение минимальной цены
# Далее отправляем за получением максимальной цены
def get_min_price(message, user: classes.Person):
    # Проверяем что в сообщении цифры
    if message.text.isdigit():
        # Запоминаем максимальнгую цену
        user.min_price = message.text
        #functions.hist[message.chat.id][now].min_price = message.text
        bot.send_message(message.from_user.id, "Напишите максимальную стоимость (USD)")
        bot.register_next_step_handler(message, get_max_price, user)
    # Если в сообщении не цифры, переспрашиваем
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только цифры для ответа')
        bot.register_next_step_handler(message, get_min_price)


# Получение максимальной цены
# Далее отправляем за радиусом поиска
def get_max_price(message, user: classes.Person):
    # Проверяем что в сообщении цифры
    if message.text.isdigit():
        # Запоминаем максимальнгую цену
        user.max_price = message.text
        #functions.hist[message.chat.id][now].max_price = message.text
        bot.send_message(message.from_user.id, "Напишите радиус поиска (в милях)")
        bot.register_next_step_handler(message, get_radius, user)
    # Если в сообщении не цифры, переспрашиваем
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только цифры для ответа')
        bot.register_next_step_handler(message, get_max_price, user)


# Получение радиуса
# Далее отправляем за названием города
def get_radius(message, user: classes.Person):
    # Проверяем что в сообщении цифры
    if message.text.isdigit():
        # Запоминаем радиус поиска
        user.radius = message.text
        bot.send_message(message.from_user.id, "Напишите название города")
        bot.register_next_step_handler(message, check, user)
    # Если в сообщении не цифры, переспрашиваем
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только числа для ответа')
        bot.register_next_step_handler(message, get_radius, user)

# Проверяем, существует ли такой город в базе
def check(message, user: classes.Person):
    check_id = classes.API()
    if (check_id.query_id_city(message.text)).isdigit():
        get_city(message, user)
    elif message.text[0] == '/':
        bot.send_message(message.from_user.id, 'Не надо вводить команды. Напишите название города')
        bot.register_next_step_handler(message, check, user)

    else:
        bot.send_message(message.from_user.id, 'Такого города нет в базе. Напишите название города')
        bot.register_next_step_handler(message, check, user)

# Получение названия города от пользователя
# Далее отправляем за получением количества отелей
def get_city(message, user: classes.Person):
    # Запоминаем название города
    user.city = message.text
    #functions.hist[message.chat.id][now].city = message.text
    bot.send_message(message.from_user.id, 'Напишите количество отелей (не более 20)')
    bot.register_next_step_handler(message, get_nums, user)


# Получение кол-ва отелей от пользователя
# Даем пользователю клавиатуру с возможностью выбора вариантов
# Далее отправляем на обработку кнопок с клавиатуры
def get_nums(message, user: classes.Person):
    # Проверка на цифры в сообщении
    if message.text.isdigit():
        # Запоминаем кол-во отелей
        user.num_city = message.text
        #functions.hist[message.chat.id][now].num_city = message.text
        # Клавиатура с вопросом о фото
        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = 'Результаты нужны с фотографиями?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

        # Обработка нажатий кнопок на клавиатуре
        @bot.callback_query_handler(func=lambda call: True)
        def callback_worker(call):
            # Если ответ был "да", отправляем за количеством фотографий
            if call.data == "yes":
                bot.send_message(call.message.chat.id, 'Напишите количество фотографий для каждого отеля (не более 5)')
                # Удаляем клавиатуру после нажатия
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                bot.register_next_step_handler(call.message, get_photo, user)

            # Если фото не нужны, выводим результаты поиска
            elif call.data == "no":
                # Удаляем клавиатуру после нажатия
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
                # Выводим результат
                get_result(user, call.message.chat.id)

    # Если в сообщении не цифры, задаем вопрос заново
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только цифры для ответа')
        bot.register_next_step_handler(message, get_nums, user)

# Получение кол-ва фотографий от пользователя
def get_photo(message, user: classes.Person):
    if message.text.isdigit():
        #Запоминаем количество фото
        user.nums_photo = message.text
        # Выводим результат
        get_result(user, message.chat.id)
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только цифры для ответа')
        bot.register_next_step_handler(message, get_photo, user)

def get_result(user: classes.Person, id: int):
    bot.send_message(id, 'Ожидайте')
    output = classes.API()  # Создаем объект класса для обращения к API

    # Если выбирали функцию /bestdeal, запускаем ее
    if user.choice == '/bestdeal':
        hotels = output.bestdeal(nums=user.num_city,
                                 city=user.city,
                                 min_price=user.min_price,
                                 radius=user.radius,
                                 max_price=user.max_price)
    # Если выбирали функцию /highprice или /lowprice, запускаем поиск без доп.параметров
    else:
        hotels = output.searchprice(nums=user.num_city,
                                    city=user.city,
                                    choise=user.choice)

    # Если произошла ошибка соединения, то результатом работы будет строка с сообщением об ошибке
    if type(hotels) == str:
        bot.send_message(id, hotels)

    else:
        # Выводим информацию об отелях
        for i in hotels:
            info = classes.Hotels(i)
            bot.send_message(id, info.__str__())
            # Добавляем название отеля в историю
            user.hotels.append(info)
        # Добавляем информацию о поиске в базу данных
        sql_connection.add_user(user)



# Для непрерывной работы бота
bot.polling(none_stop=True, interval=0)
