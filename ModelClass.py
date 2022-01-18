from email import message
from ViewClasses import *
import pymysql
from datetime import datetime 
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
        query = "select * from users where email=%s AND user_pass=%s and user_status = %s"
        args = (email,password,True)
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
        query = 'INSERT INTO users VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        args = (new_user["username"],new_user["email"],new_user["user_pass"],new_user["user_status"],new_user["user_key"],
        new_user["date_joined"],new_user["dob"],new_user["gender"],new_user["location"],new_user["address"],
        new_user["profile_picture"])
        success = self.dml_run(query,args,'insert')
        return True if (success == True) else False
    
    def confirmation(self, key, email):
        query = 'select user_key from users where email = %s'
        args = email
        user_key = self.dml_run(query,args,'get')
        if user_key[0]["user_key"] == key:
            query = 'update users set user_status = %s where email = %s'
            args = (True, email)
            success= self.dml_run(query,args,'insert')
            return True if (success == True) else False
        return False
    
    def add_diary(self, new_user):
        query = 'INSERT INTO diaries(email,page_count,diary_type) VALUES (%s,%s,%s)'
        args = (new_user["email"],0,new_user["type"])
        success = self.dml_run(query,args,'insert')
        return True if (success == True) else False
    
    def add_page(self, new_user):
        query = 'select page_count,diary_id from diaries where email = %s'
        args = new_user["email"]
        data = self.dml_run(query,args,'get')
        query = 'INSERT INTO pages(email,diary_id, page_date, visible_status, content_text,content_video_pic, is_content_video) VALUES (%s,%s,%s,%s,%s,%s,%s)'
        args = (new_user["email"],data[0]["diary_id"],new_user["page_date"],new_user["visible_status"],new_user["content_text"],new_user["content_video_pic"], new_user['is_content_video'])
        print("IS CONTENT VIDEO: ",new_user["is_content_video"])
        success = self.dml_run(query,args,'insert')
        print(success, 'Something went wrong here')
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
    
    def get_explore_pages(self,new_user):
        query = 'select email,username,profile_picture from users where email != %s'
        args = new_user
        public_email = self.dml_run(query,args,'get')
        query = 'select * from pages where email != %s and visible_status=%s order by page_date DESC'
        args = (new_user,True) 
        Ulist = self.dml_run(query,args,'get')
        query = 'select * from page_interaction where follower_email = %s'
        args = (new_user) 
        likeList = self.dml_run(query,args,'get')
        for i in Ulist:
            query = 'select MAX(like_count) AS "like_count" from page_interaction where page_id = %s '
            args = i["page_id"]
            count = self.dml_run(query,args,'get')
            if bool(count[0]["like_count"]):
                i['count'] = count[0]["like_count"]
            else:
                i['count'] = 0
            for j in public_email:
                if i['email'] == j['email']:
                    i['profile_picture'] = str(f'http://127.0.0.1:5000/profile_picture/{j["email"]}')
                    i['username'] = j['username']
            if bool(likeList):
                for j in likeList:
                    if i['page_id'] == j['page_id']:
                        i['liked'] = True
                        break
                    else:
                        i['liked'] = False
        return Ulist
    
    def search_user(self,name,email):
        query = 'select * from users where username like %s and email != %s'
        args = ('%'+name+'%', email)
        public_users = self.dml_run(query,args,'get')
        if bool(public_users):
            for i in public_users:
                i['profile_picture'] = str(f'http://127.0.0.1:5000/profile_picture/{i["email"]}')
        return public_users if (bool(public_users)) else list()

    def add_follower(self,user,followed_user):
        query = 'select * from followers where email = %s and followed_user = %s'
        args = (user, followed_user)
        record = self.dml_run(query,args,'get')
        flag = None
        if bool(record):
            query = 'delete from followers where email = %s and followed_user = %s'
            args = (user, followed_user)
            success = self.dml_run(query,args,'insert')
            if success == True:
                flag = 1 
        else:
            query = 'INSERT INTO followers(email,followed_user) VALUES (%s,%s)'
            args = (user,followed_user)
            success = self.dml_run(query,args,'insert')
            if success == True:
                flag = 0 
        return flag
    
    def get_followers(self,user):
        query = 'select email from followers where followed_user = %s'
        args = (user)
        followers = self.dml_run(query,args,'get')
        if bool(followers):
            for i in followers:
                i['profile_picture'] = str(f'http://127.0.0.1:5000/profile_picture/{i["email"]}')
        return followers if (bool(followers)) else list()
    
    def set_like(self,interact):
        query = 'select MAX(like_count) AS "like_count" from page_interaction where page_id = %s '
        args = interact["page_id"]
        count = self.dml_run(query,args,'get')
        number = 0
        if bool(count[0]["like_count"]):
            number = count[0]["like_count"] + 1
        else:
            number = 1
        query = 'INSERT INTO page_interaction(follower_email,page_id,interaction_date,like_count) VALUES (%s,%s,%s,%s)'
        args = (interact["email"], interact["page_id"], interact["date"], number)
        success = self.dml_run(query,args,'insert')
        return True if (success == True) else False
    
    def update_chat(self,user):
        query = 'select COUNT(%s) As count from chat'
        args = 'email'
        flag = None
        count = self.dml_run(query,args,'get')
        if bool(count) and count[0]["count"]>=500:
            query = 'delete from chat'
            args = None
            success_delete = self.dml_run(query,args,'insert')
            if success_delete:
                query = 'INSERT INTO chat VALUES (%s,%s,%s,%s)'
                args = (user["currentUser"]["email"], user["currentUser"]["username"], user["currentUser"]["profile_picture"], user["message"])
                success = self.dml_run(query,args,'insert')
                if success:
                    flag = 0
        else:
            query = 'INSERT INTO chat VALUES (%s,%s,%s,%s)'
            args = (user["currentUser"]["email"], user["currentUser"]["username"], user["currentUser"]["profile_picture"], user["message"])
            success = self.dml_run(query,args,'insert')
            if success:
                flag = 1
        return flag
    
    def get_chat(self):
        query = 'select * from chat'
        args = None
        messages = self.dml_run(query,args,'get')
        actual_list = list()
        for i in messages:
            element = {"currentUser":None, "message":None}
            sub_dict = dict()
            sub_dict["email"] = i["email"]
            sub_dict["username"] = i["username"]
            sub_dict["profile_picture"] = i["profile_picture"]
            element['currentUser'] = sub_dict
            element['message'] = i["text_data"]
            actual_list.append(element)
        return actual_list if bool(actual_list) else list()

    def get_follower_pages(self,new_user):
        query = 'select email,username,profile_picture from users where email in (select followed_user from followers where email = %s)'
        args = new_user
        public_email = self.dml_run(query,args,'get')
        query = 'select * from pages where email in (select followed_user from followers where email = %s) and visible_status=%s order by page_date DESC'
        args = (new_user,True) 
        Ulist = self.dml_run(query,args,'get')
        query = 'select * from page_interaction where follower_email = %s'
        args = (new_user) 
        likeList = self.dml_run(query,args,'get')
        for i in Ulist:
            query = 'select MAX(like_count) AS "like_count" from page_interaction where page_id = %s '
            args = i["page_id"]
            count = self.dml_run(query,args,'get')
            if bool(count[0]["like_count"]):
                i['count'] = count[0]["like_count"]
            else:
                i['count'] = 0
            for j in public_email:
                if i['email'] == j['email']:
                    i['profile_picture'] = str(f'http://127.0.0.1:5000/profile_picture/{j["email"]}')
                    i['username'] = j['username']
            if bool(likeList):
                for j in likeList:
                    if i['page_id'] == j['page_id']:
                        i['liked'] = True
                        break
                    else:
                        i['liked'] = False
        return Ulist