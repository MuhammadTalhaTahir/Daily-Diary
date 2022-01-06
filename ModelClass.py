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
            #self.connection.autocommit(True)
        except Exception as e:
            print("There is error in connection.", str(e))

    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    def dml_run(self,query,args,qtype):
        data = None
        flag = False
        try:
            if self.connection is not None:
                cursor = self.connection.cursor(pymysql.cursors.DictCursor)
                cursor.execute(query,args)
                if qtype == 'get':
                    data = cursor.fetchall()
                elif qtype == 'insert':
                    flag = True
        except Exception as e:
            print("Exception in DML Run.", str(e))
        finally:
            if cursor is not None:
                cursor.close()
            if qtype == 'get': 
                return data
            elif qtype == 'insert':
                self.connection.commit()
                return flag
            
    def login(self, email, password):
        query = "select * from users where email=%s AND user_pass=%s"
        args = (email,password)
        user_list = None
        user_list = self.dml_run(query,args,'get')
        return user_list if (bool(user_list)) else list()
    
    def profile_picture(self, email):
        query = "select profile_picture from users where email = %s"
        args = email
        picture_path = self.dml_run(query,args,"get")
        return picture_path[0]["profile_picture"] if(picture_path!=None) else ""

    def user_exist(self, email):
        query = "select * from users where email = %s"
        args = email
        user_data = None
        user_data = self.dml_run(query,args, 'get')
        return True if (bool(user_data)) else False
    
    def register(self, new_user):
        query = 'INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        args = (new_user["username"],new_user["email"],new_user["user_pass"],new_user["user_status"],
        new_user["date_joined"],new_user["dob"],new_user["gender"],new_user["location"],new_user["address"],
        new_user["profile_picture"])
        success = self.dml_run(query,args,'insert')
        return True if (success == True) else False
    
    def add_diary(self, new_user):
        query = 'INSERT INTO diaries VALUES (%s,%s,%s)'
        args = (new_user["email"],0,new_user["type"])
        success = self.dml_run(query,args,'insert')
        return True if (success == True) else False
    
    def add_page(self, new_user):
        query = 'select page_count,diary_id from diaries where email = %s'
        args = new_user["email"]
        data = self.dml_run(query,args,'get')
        query = 'INSERT INTO pages VALUES (%s,%s,%s,%s,%s,%s)'
        args = (new_user["email"],data[0]["diary_id"],new_user["page_date"],new_user["visible_status"],
        new_user["content_text"],new_user["content_video_pic"])
        success = self.dml_run(query,args,'insert')
        if success:
            query = 'update diaries set page_count = %s where diary_id = %s'
            args = ((data[0]["page_count"]+1),data[0]["diary_id"])
            success1 = self.dml_run(query,args,'insert')
            return True if (success1 == True) else False
        return False

    def get_pages(self, new_user):
        query = 'select * from pages where email = %s'
        args = new_user
        page_list = None
        page_list = self.dml_run(query,args,'get')
        return page_list if (bool(page_list)) else list()
