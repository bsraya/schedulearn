import re
from dataclasses import dataclass
from pydantic import BaseModel
from pydantic.dataclasses import dataclass

# password should be at least 8 characters
# password should contain at least one number
# password should contain at least one capital letter
PASSWORD_REGEX = r'^(?=.*[A-Z])(?=.*[0-9])(?=.{8,})'

# johndoe@gmail.com
# johndoe@gapp.nthu.edu.tw
# johndoe@office365.nthu.edu.tw
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

class UserLogin(BaseModel):
    username: str
    password: str

class SignupForm(BaseModel):
    first_name: str
    last_name: str
    email: str
    username: str
    password: str

    def is_valid_email(self, email):
        if re.match(EMAIL_REGEX, email):
            return True
        return False
    
    def is_valid_password(self, password):
        if re.match(PASSWORD_REGEX, password):
            return True
        return False

    def is_valid(self):
        errors = {
            "first_name": [],
            "last_name": [],
            "email": [],
            "username": [],
            "password": []
        }
        if not self.first_name or not len(self.first_name) > 1:
            errors["first_name"].append("First name is required")
        if not self.last_name or not len(self.last_name) > 1:
            errors["last_name"].append("Last name is required")
        if not self.username or not len(self.username) > 1:
            errors["username"].append("Username is required")    
        if not self.email: 
            errors["email"].append("Email is required")
        if not self.is_valid_email(self.email):
            errors["email"].append("Email is invalid")
        if not self.password:
            errors["password"].append("Password is required")
        if not self.is_valid_password(self.password):
            errors["password"].append("Password is invalid")
        if errors["first_name"] or errors["last_name"] or errors["email"] or errors["username"] or errors["password"]:
            return False, errors
        return True, errors
