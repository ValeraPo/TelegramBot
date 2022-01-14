hist = dict()  # Словарь для хранения истории запросов


# Функция для вывода истории
def history(id_chat) -> str:
    # Проверяем, не пустая ли история
    if len(hist[id_chat]) == 0:
        return 'История пустая'
    # Выводим сообщения
    result = str()
    for time, search in hist[id_chat].items():
        result += str(time) + '\n'  # Время обращения
        result += str(search.choise) + '\n'  # Функция
        result += str(search.city) + '\n'  # Город поиска

        # Результаты поиска
        for i in search.hotels:
            result += str(i) + '\n'
        result += '\n'
    return result
