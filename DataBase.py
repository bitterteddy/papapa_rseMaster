import mysql.connector

class Database:
    def __init__(self, user, password, host, database, url, date):
        self.__connection = mysql.connector.connect(user=user, password=password,
                              host=host,
                              database=database)
        # далее код провер€ет наличие таблиц History и Results в Ѕƒ и при необходимости добавл€ет их
        # далее код провер€ет наличие текущего запроса в History (добавл€ет его) и получает его id
        self.__id = 0
    

    #ƒобавл€ет строку в таблицу results
    def add_result(self):
        return true

    def __del__(self):
        self.__connection.close()




