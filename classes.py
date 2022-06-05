import os
import requests
import json


# Класс для структурирования и вывода информации об отеле
class Hotels:
    def __init__(self, result_dict: dict):
        self.name = result_dict['name']  # Название отеля
        self.price = result_dict['ratePlan']['price']['current']  # Цена
        self.radius = result_dict['landmarks'][0]['distance']  # Расстояние до центра
        self.id_hotel = str(result_dict['id'])  # id отеля, нужно для bestdeal
        self.url = f'https://ru.hotels.com/ho{self.id_hotel}/' # Ссылка на отель

    # Вывод информации. Нужно для сообщений
    def __str__(self):
        return f'Название: {self.name}\n' \
               f'Цена: {self.price}\n' \
               f'Расстояние до центра: {self.radius}\n' \
               f'{self.url}'

    # Возвращает id отеля. Нужно для bestdeal
    def get_id_hotel(self) -> str:
        return self.id_hotel


# Класс для работы с API
class API:

    # Header для соединения с сайтом
    def get_headers(self) -> dict:
        return {
            'x-rapidapi-key': os.getenv('API_TOKEN'),
            'x-rapidapi-host': "hotels4.p.rapidapi.com"
        }

    # Поиск id города по названию введеному пользователем
    def query_id_city(self, city) -> str:
        url = "https://hotels4.p.rapidapi.com/locations/search"
        querystring = {"query": city, "locale": "en_US"}

        # Попытка соединения
        try:

            response_id = requests.request("GET", url, headers=self.get_headers(),
                                           params=querystring, timeout=10)
            response_id = json.loads(response_id.text)

            result = response_id["suggestions"][0]["entities"][0]["destinationId"]
        # Обработка ошибок
        except IndexError:
            result = "Такого города не существует. Проверьте правильность написания."
        except ConnectionError:
            result = "Ошибка соединения с сервером. Повторите попытку позднее"
        except requests.ReadTimeout:
            result = "Время ожидания превысило."

        return result

    # Поиск отелей
    def searchprice(self, city, choise='/lowprice',
                    nums='25', min_price='0', max_price='0') -> dict:

        # highprice сортируется по убыванию цены
        if choise == '/highprice':
            sort = 'PRICE_HIGHEST_FIRST'
        # besteal сортируется по расстоянию до центра
        elif choise == '/bestdeal':
            sort = 'DISTANCE_FROM_LANDMARK'
        # lowprice сщртируется по возрастанию цены
        else:
            sort = "PRICE"

        city_id = self.query_id_city(city)  # Превращение названия города в id
        url = "https://hotels4.p.rapidapi.com/properties/list"
        querystring = {
            "destinationId": city_id,
            "pageNumber": "1",
            "pageSize": nums,
            "checkIn": "2020-01-08",
            "checkOut": "2020-01-15",
            "adults1": "1",
            "sortOrder": sort,
            "locale": "en_US",
            "currency": "USD"
        }
        # Если bestdeal, то добавляем в запрос диапазон цен
        # и сортируем по расстоянию до центра
        if max_price != '0':
            querystring['priceMin'] = min_price
            querystring['priceMax'] = max_price
            querystring['landmarkIds'] = 'City center'

        # Попытка соединения
        try:
            response = requests.request("GET", url, headers=self.get_headers(), params=querystring, timeout=10)
            response = json.loads(response.text)
            result = response['data']['body']['searchResults']['results']
        except ConnectionError:
            result = "Ошибка соединения с сервером. Повторите попытку позднее"
        except requests.ReadTimeout:
            result = "Время ожидания превысило."

        # Возвращаем json или сообщение об ошибке
        return result

    # Поиск отелей в заданном ценовом диапазоне и радиусе
    def bestdeal(self, min_price, max_price, radius, nums, city) -> dict:
        hotels = self.searchprice(city=city, min_price=min_price,
                                  max_price=max_price, nums=nums, choise = '/bestdeal')
        # Оставляем только результаты, подходящие по радиусу
        result = []
        for i in hotels:
            info = Hotels(i)
            distance = info.radius.split()
            if distance[0] is None:
                distance[0] = 0
            distance = float(distance[0])
            if float(radius) >= distance:
                result.append(i)

        return result

    # Запрос фото
    def photo(self, num, id_hotel) -> str:
        url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

        querystring = {"id": id_hotel}

        try:
            response = requests.request("GET", url, headers=self.get_headers(), params=querystring, timeout=10)
            response = json.loads(response.text)
            # Сохраняем необходимое количество ссылок на фото в список
            result = []
            for i in range(num):
                img = response["hotelImages"][i]["baseUrl"]
                result.append(img.format(size='z'))
        except ConnectionError:
            result = "Ошибка соединения с сервером. Повторите попытку позднее"
        except requests.ReadTimeout:
            result = "Время ожидания превысило."

        return result


# Класс пользователя, который хранит информацию о поиске
class Person:

    def __init__(self):
        self.time = None # Время поиска
        self.id_chat = None # Id чата
        self.choice = None  # Название функции, выбранной пользователем
        self.city = None  # Название города
        self.min_price = None  # Минимальная цена
        self.max_price = None  # Максимальная цена
        self.radius = None  # Расстояние до центра
        self.num_city = None  # Кол-во отелей
        self.nums_photo = None  # Кол-во фотографий
        self.hotels = list()  # Результат поиска

