import mysql.connector

class Database:
    def __init__(self, user, password, host, database, url, date):
        self.__connection = mysql.connector.connect(user=user, password=password,
                              host=host,
                              database=database)
        # ����� ��� ��������� ������� ������ History � Results � �� � ��� ������������� ��������� ��
        # ����� ��� ��������� ������� �������� ������� � History (��������� ���) � �������� ��� id
        self.__id = 0
    

    #��������� ������ � ������� results
    def add_result(self):
        return true

    def __del__(self):
        self.__connection.close()




