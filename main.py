import telebot
import os
from dotenv import load_dotenv
from telebot import types
from datetime import datetime
import classes
import functions
import collections

load_dotenv()

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))


@bot.message_handler(content_types=['text'])
# Обработка сообщений от пользователя
def start(message):
    # Если бот еще не общался с пользователем, добавляем его id  в словарь для истории
    if message.chat.id not in functions.hist:
        functions.hist[message.chat.id] = collections.OrderedDict()

    # Реализация функций поиска отелей
    if message.text.lower() == '/lowprice' or message.text.lower() == '/highprice' or message.text.lower() == '/bestdeal':

        # Добавляем запись в историю
        now = datetime.now().strftime('%H:%M, %d.%m.%Y')
        # Создаем объект класса Person
        functions.hist[message.chat.id][now] = classes.Person()
        functions.hist[message.chat.id][now].choise = message.text.lower()  # Запоминаем выбор

        # Функция /bestdeal
        # Для получения данных для поиска отправляем сначала в get_min_price за минимальной ценой
        if message.text.lower() == '/bestdeal':
            bot.send_message(message.from_user.id, "Напишите минимальную стоимость (USD)")
            bot.register_next_step_handler(message, get_min_price, now)
        # Функции lowprice и highprice
        # Для получения данных для поиска отправляем сразу в get_city за получением города
        else:
            bot.send_message(message.from_user.id, "Напишите название города")
            bot.register_next_step_handler(message, check, now)
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
        text = functions.history(message.chat.id)
        bot.send_message(message.from_user.id, text)

    # Обработка остальных сообщений пользователя
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /start или /help")


# Получение минимальной цены
# Далее отправляем за получением максимальной цены
def get_min_price(message, now):
    # Проверяем что в сообщении цифры
    if message.text.isdigit():
        # Запоминаем максимальнгую цену
        functions.hist[message.chat.id][now].min_price = message.text
        bot.send_message(message.from_user.id, "Напишите максимальную стоимость (USD)")
        bot.register_next_step_handler(message, get_max_price, now)
    # Если в сообщении не цифры, переспрашиваем
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только цифры для ответа')
        bot.register_next_step_handler(message, get_min_price, now)


# Получение максимальной цены
# Далее отправляем за радиусом поиска
def get_max_price(message, now):
    # Проверяем что в сообщении цифры
    if message.text.isdigit():
        # Запоминаем максимальнгую цену
        functions.hist[message.chat.id][now].max_price = message.text
        bot.send_message(message.from_user.id, "Напишите радиус поиска (в милях)")
        bot.register_next_step_handler(message, get_radius, now)
    # Если в сообщении не цифры, переспрашиваем
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только цифры для ответа')
        bot.register_next_step_handler(message, get_max_price, now)


# Получение радиуса
# Далее отправляем за названием города
def get_radius(message, now):
    # Проверяем что в сообщении цифры
    if message.text.isdigit():
        # Запоминаем радиус поиска
        functions.hist[message.chat.id][now].radius = message.text
        bot.send_message(message.from_user.id, "Напишите название города")
        bot.register_next_step_handler(message, check, now)
    # Если в сообщении не цифры, переспрашиваем
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только числа для ответа')
        bot.register_next_step_handler(message, get_radius, now)


def check(message, now):
    check_id = classes.API()
    if (check_id.query_id_city(message.text)).isdigit():
        get_city(message, now)
    elif message.text[0] == '/':
        bot.send_message(message.from_user.id, 'Не надо вводить команды. Напишите название города')
        bot.register_next_step_handler(message, check, now)

    else:
        bot.send_message(message.from_user.id, 'Такого города нет в базе. Напишите название города')
        bot.register_next_step_handler(message, check, now)


# Получение названия города от пользователя
# Далее отправляем за получением количества отелей
def get_city(message, now):

    # Запоминаем название города
    functions.hist[message.chat.id][now].city = message.text
    bot.send_message(message.from_user.id, 'Напишите количество отелей (не более 20)')
    bot.register_next_step_handler(message, get_nums, now)


# Получение кол-ва отелей от пользователя
# Даем пользователю клавиатуру с возможностью выбора вариантов
# Далее отправляем на обработку кнопок с клавиатуры
def get_nums(message, now):
    # Проверка на цифры в сообщении
    if message.text.isdigit():
        # Запоминаем кол-во отелей
        functions.hist[message.chat.id][now].num_city = message.text
        # Клавиатура с вопросом о фото
        keyboard = types.InlineKeyboardMarkup()  # наша клавиатура
        key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')  # кнопка «Да»
        keyboard.add(key_yes)  # добавляем кнопку в клавиатуру
        key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
        keyboard.add(key_no)
        question = 'Результаты нужны с фотографиями?'
        bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)
    # Если в сообщении не цифры, задаем вопрос заново
    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только цифры для ответа')
        bot.register_next_step_handler(message, get_nums, now)


# Обработка нажатий кнопок на клавиатуре
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    # Вводим параметр времени для передачи в следующие функции
    # Время обращения - последний ключ в словаре пользователя
    now = next(reversed(functions.hist[call.message.chat.id]))
    # Если ответ был "да", отправляем за количеством фотографий
    if call.data == "yes":
        bot.send_message(call.message.chat.id, 'Напишите количество фотографий для каждого отеля (не более 5)')
        # Удаляем клавиатуру после нажатия
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.register_next_step_handler(call.message, get_photo, now)

    # Если фото не нужны, выводим результаты поиска
    elif call.data == "no":
        bot.send_message(call.message.chat.id, 'Ожидайте')
        # Удаляем клавиатуру после нажатия
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        output = classes.API()  # Создаем объект класса для обращения к API

        # Если выбирали функцию /bestdeal, запускаем ее
        if functions.hist[call.message.chat.id][now].choise == '/bestdeal':
            hotels = output.bestdeal(nums=functions.hist[call.message.chat.id][now].num_city,
                                     city=functions.hist[call.message.chat.id][now].city,
                                     min_price=functions.hist[call.message.chat.id][now].min_price,
                                     radius=functions.hist[call.message.chat.id][now].radius,
                                     max_price=functions.hist[call.message.chat.id][now].max_price)
        # Если выбирали функцию /highprice или /lowprice, запускаем поиск без доп.параметров
        else:
            hotels = output.searchprice(nums=functions.hist[call.message.chat.id][now].num_city,
                                        city=functions.hist[call.message.chat.id][now].city,
                                        choise=functions.hist[call.message.chat.id][now].choise)

        # Если произошла ошибка соединения, то результатом работы будет строка с сообщением об ошибке
        if type(hotels) == str:
            bot.send_message(call.message.chat.id, hotels)

        else:
            # Выводим информацию об отелях
            for i in hotels:
                info = classes.Hotels(i)
                bot.send_message(call.message.chat.id, info.__str__())
                # Добавляем название отеля в историю
                functions.hist[call.message.chat.id][now].hotels.append(info.name)
                functions.hist[call.message.chat.id][now].hotels.append(info.url)



# Получение кол-ва фотографий от пользователя
def get_photo(message, now):
    if message.text.isdigit():
        functions.hist[message.chat.id][now].nums_photo = message.text
        # nums_photo = message.text
        bot.send_message(message.from_user.id, 'Ожидайте')
        output = classes.API()
        hotels = output.searchprice(nums=functions.hist[message.chat.id][now].num_city,
                                    city=functions.hist[message.chat.id][now].city,
                                    choise=functions.hist[message.chat.id][now].choise)

        # Если произошла ошибка соединения, то результатом работы будет строка с сообщением об ошибке
        if type(hotels) == str:
            bot.send_message(call.message.chat.id, hotels)

        else:
            # Выводим информацию об отелях
            for i in hotels:
                info = classes.Hotels(i)
                bot.send_message(message.from_user.id, info.__str__())
                # Добавляем название отеля в историю
                functions.hist[message.chat.id][now].hotels.append(info.name)
                id_hotel = info.id_hotel
                photos = output.photo(num=int(functions.hist[message.chat.id][now].nums_photo), id_hotel=id_hotel)

                # Выводим фотографии каждого отеля
                for j in photos:
                    bot.send_photo(message.from_user.id, j)

    else:
        bot.send_message(message.from_user.id, 'Допустимо использовать только цифры для ответа')
        bot.register_next_step_handler(message, get_photo, now)


# Для непрерывной работы бота
bot.polling(none_stop=True, interval=0)
