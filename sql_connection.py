import pyodbc

import classes

conn = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=DESKTOP-VNQJ52K\SQLEXPRESS;'
                      'Database=TeleBot;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()

def add_user(user: classes.Person):
    cursor.execute(f''' INSERT INTO [TeleBot].[dbo].[Searches] 
                                  (id_chat, 
                                  time, 
                                  func,
                                  city) 
                                VALUES 
                                  ({user.id_chat}, 
                                  '{user.time}', 
                                  '{user.choice}',
                                  N'{user.city}') ''')
    conn.commit()
    cursor.execute(f'''SELECT scope_identity()''')
    id = cursor.fetchone()[0]
    for i in user.hotels:
        add_hotel(id, i)


def add_hotel(id_search: int, hotel: classes.Hotels):
    cursor.execute(f'''INSERT INTO Hotels 
                                  (id_search, 
                                  name, 
                                  link)
                                  output inserted.ID 
                                VALUES 
                                  ({id_search}, 
                                  N'{hotel.name}', 
                                  N'{hotel.url}') ''')
    conn.commit()

def get_history(id_chat):
    cursor.execute(f'''SELECT id, time, func, city
                                        FROM Searches
                                        WHERE id_chat = {id_chat}''')
    table = cursor.fetchall()
    res = ''
    for i in table:
        res += str(i[1]) + '\n'  # time
        res += str(i[2]) + '\n'  # func
        res += str(i[3]) + '\n'  # city
        res += get_hotels(i[0])

    return res

def get_hotels(id_search):
    cursor.execute(f'''SELECT name, link
                                        FROM Hotels
                                        WHERE id_search = {id_search}''')
    table = cursor.fetchall()
    res = ''
    for i in table:
        res += str(i[0]) + '\n'  # name
        res += str(i[1]) + '\n'  # link
    return res + '\n'

def get_all_users():
    cursor.execute(f'''SELECT id_chat
                        FROM Users''')
    return cursor.fetchall()

user = classes.Person()

user.city = 'Москва'
user.id_chat = 1414
user.time = '12.12.12'
user.choice = '/lowprice'
#add_user(user)

# get_history(22)
# print('_____________')
# cursor.execute('SELECT * FROM Searches')
# for i in cursor:
#     print(i)
#
# cursor.execute('SELECT * FROM Hotels')
# for i in cursor:
#     print(i)
