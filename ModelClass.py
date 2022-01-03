from ViewClasses import *
import pymysql 
import pymysql.cursors
class Model:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        try:
            self.connection = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                              database=self.database)
        except Exception as e:
            print("There is error in connection.", str(e))

    def __del__(self):
        if self.connection!= None:
            self.connection.close()

    def dml_run(self,query,args):
        data = None
        try:
            if self.connection != None:
                cursor = self.connection.cursor(pymysql.cursors.DictCursor)
                cursor.execute(query,args)
                data = cursor.fetchall()
        except Exception as e:
            print("Exception in CheckUserExist.", str(e))
        finally:
            if cursor is not None:
                cursor.close()
            return data
            
    def login(self, email, password):
        query = "select * from users where email=%s AND user_pass=%s"
        args = (email,password)
        user_list = None
        user_list = self.dml_run(query,args)
        if user_list != None:
            return user_list
        return False



    
