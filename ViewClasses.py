class user:
    def __init__(self,user_data=None):
        if user_data is not None:
            self.username = user_data["username"]
            self.email = user_data["email"]
            self.user_pass = user_data["user_pass"]
            self.user_status = user_data["user_status"]
            self.date_joined = user_data["date_joined"]
            self.dob = user_data["dob"]
            self.gender = user_data["gender"]
            self.location = user_data["location"]
            self.address = user_data["address"]
            self.profile_picture = user_data["profile_picture"]
        else:
            self.username = ""
            self.email = ""
            self.user_pass = ""
            self.user_status = ""
            self.date_joined = ""
            self.dob = ""
            self.gender = ""
            self.location = ""
            self.address = ""
            self.profile_picture = ""

    